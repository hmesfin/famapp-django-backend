"""
API tests for the invitations app
TDD approach - these tests drove our API implementation!
"""
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from apps.invitations.models import Invitation
from apps.permissions.models import Role, Permission
from apps.permissions.constants import RoleCodeName, PermissionCodeName

User = get_user_model()


class InvitationAPITests(APITestCase):
    """Test suite for invitation API endpoints"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create manager role and permission
        self.send_invitations_permission = Permission.objects.create(
            code_name=PermissionCodeName.SEND_INVITATIONS,
            name='Send Invitations',
            description='Can send invitations to new users'
        )
        
        self.manager_role = Role.objects.create(
            code_name=RoleCodeName.MANAGER,
            name='Manager',
            description='Manager role with invitation permissions'
        )
        self.manager_role.permissions.add(self.send_invitations_permission)
        
        # Create inviter with manager role so they can send invitations
        self.inviter = User.objects.create_user(
            email='inviter@example.com',
            password='testpass123'
        )
        self.inviter.assign_role(self.manager_role)
        
        self.other_user = User.objects.create_user(
            email='other@example.com',
            password='testpass123'
        )
        
        # Authenticate the inviter
        refresh = RefreshToken.for_user(self.inviter)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
    def test_create_invitation(self):
        """Test creating an invitation via API"""
        data = {
            'email': 'newuser@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'role': 'member',
            'organization_name': 'Test Company',
            'message': 'Welcome to our team!'
        }
        
        response = self.client.post('/api/invitations/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], 'newuser@example.com')
        self.assertEqual(response.data['status'], 'pending')
        self.assertIn('invitation_url', response.data)
        
    def test_cannot_invite_existing_user(self):
        """Test that you cannot send invitation to existing user"""
        data = {
            'email': 'other@example.com',  # Already exists
            'first_name': 'Jane',
            'last_name': 'Smith',
            'role': 'member'
        }
        
        response = self.client.post('/api/invitations/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already registered', str(response.data).lower())
        
    def test_list_invitations_sent(self):
        """Test listing invitations sent by the user"""
        # Create some invitations
        Invitation.objects.create(
            email='user1@example.com',
            invited_by=self.inviter
        )
        Invitation.objects.create(
            email='user2@example.com',
            invited_by=self.inviter
        )
        Invitation.objects.create(
            email='user3@example.com',
            invited_by=self.other_user  # Different inviter
        )
        
        response = self.client.get('/api/invitations/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if response is paginated or not
        if isinstance(response.data, dict) and 'results' in response.data:
            # Paginated response
            self.assertEqual(len(response.data['results']), 2)
        else:
            # Non-paginated response
            self.assertEqual(len(response.data), 2)
        
    def test_resend_invitation_api(self):
        """Test resending an invitation via API"""
        invitation = Invitation.objects.create(
            email='newuser@example.com',
            invited_by=self.inviter
        )
        
        response = self.client.post(f'/api/invitations/{invitation.public_id}/resend/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Invitation resent successfully')
        
    def test_accept_invitation_api(self):
        """Test accepting an invitation via API (public endpoint)"""
        invitation = Invitation.objects.create(
            email='newuser@example.com',
            invited_by=self.inviter,
            role='member'
        )
        
        # Remove authentication for public endpoint
        self.client.credentials()
        
        data = {
            'token': invitation.token,
            'password': 'newpassword123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = self.client.post('/api/invitations/accept/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        
        # Verify user was created and invitation accepted
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, 'accepted')
        
        new_user = User.objects.get(email='newuser@example.com')
        self.assertEqual(new_user.first_name, 'New')
        self.assertEqual(new_user.last_name, 'User')
        
    def test_verify_invitation_token(self):
        """Test verifying an invitation token (public endpoint)"""
        invitation = Invitation.objects.create(
            email='newuser@example.com',
            invited_by=self.inviter,
            organization_name='Test Company'
        )
        
        # Remove authentication for public endpoint
        self.client.credentials()
        
        response = self.client.get(f'/api/invitations/verify/?token={invitation.token}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'newuser@example.com')
        self.assertEqual(response.data['organization_name'], 'Test Company')
        self.assertFalse(response.data['is_expired'])
        
    def test_cancel_invitation(self):
        """Test canceling an invitation"""
        invitation = Invitation.objects.create(
            email='newuser@example.com',
            invited_by=self.inviter
        )
        
        response = self.client.delete(f'/api/invitations/{invitation.public_id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, 'cancelled')
        
    def test_cannot_resend_non_pending_invitation(self):
        """Test that only pending invitations can be resent"""
        invitation = Invitation.objects.create(
            email='newuser@example.com',
            invited_by=self.inviter
        )
        invitation.cancel()
        
        response = self.client.post(f'/api/invitations/{invitation.public_id}/resend/')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('pending', str(response.data).lower())
        
    def test_verify_with_invalid_token(self):
        """Test verifying with an invalid token"""
        # Remove authentication for public endpoint
        self.client.credentials()
        
        response = self.client.get('/api/invitations/verify/?token=invalid-token')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('invalid', str(response.data).lower())
        
    def test_verify_without_token(self):
        """Test verifying without providing a token"""
        # Remove authentication for public endpoint
        self.client.credentials()
        
        response = self.client.get('/api/invitations/verify/')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('required', str(response.data).lower())
        
    def test_accept_with_expired_token(self):
        """Test accepting an expired invitation"""
        from datetime import timedelta
        from django.utils import timezone
        
        invitation = Invitation.objects.create(
            email='newuser@example.com',
            invited_by=self.inviter
        )
        # Expire the invitation
        invitation.expires_at = timezone.now() - timedelta(days=1)
        invitation.save()
        
        # Remove authentication for public endpoint
        self.client.credentials()
        
        data = {
            'token': invitation.token,
            'password': 'newpassword123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = self.client.post('/api/invitations/accept/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('expired', str(response.data).lower())
        
    def test_user_can_only_see_own_invitations(self):
        """Test that users can only see invitations they sent"""
        # Create invitation as inviter
        Invitation.objects.create(
            email='invite1@example.com',
            invited_by=self.inviter
        )
        
        # Create invitation as other user
        Invitation.objects.create(
            email='invite2@example.com',
            invited_by=self.other_user
        )
        
        # Request as inviter
        response = self.client.get('/api/invitations/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check emails in response
        if isinstance(response.data, dict) and 'results' in response.data:
            emails = [inv['email'] for inv in response.data['results']]
        else:
            emails = [inv['email'] for inv in response.data]
        
        self.assertIn('invite1@example.com', emails)
        self.assertNotIn('invite2@example.com', emails)