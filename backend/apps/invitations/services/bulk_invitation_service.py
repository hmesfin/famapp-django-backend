"""
Bulk invitation service
Extracted from InvitationViewSet bulk_invite action

Ham Dog's Service Pattern:
- Handle complex bulk operations
- Provide detailed success/failure tracking
- Keep transaction logic clean
"""

from typing import List, Dict, Any
from django.contrib.auth import get_user_model
from django.db import transaction

from apps.invitations.models import Invitation

User = get_user_model()


class BulkInvitationService:
    """
    Handles bulk invitation operations
    
    Provides:
    - Bulk invitation creation
    - Email validation for bulk operations
    - Success/failure tracking per email
    - Transaction safety for bulk operations
    """
    
    def __init__(self):
        # Initialize InvitationService for email checking
        from .invitation_service import InvitationService
        self.invitation_service = InvitationService()
    
    def validate_emails(self, emails: List[str]) -> Dict[str, List[str]]:
        """
        Validate a list of emails for bulk invitation
        
        Args:
            emails: List of email addresses to validate
            
        Returns:
            dict: Contains 'valid' and 'invalid' email lists
        """
        valid_emails = []
        invalid_emails = []
        
        for email in emails:
            if not email or '@' not in email:
                invalid_emails.append(email)
            elif self.invitation_service.check_email_exists(email):
                invalid_emails.append(email)
            else:
                valid_emails.append(email)
        
        return {
            'valid': valid_emails,
            'invalid': invalid_emails
        }
    
    def process_bulk_invitations(
        self, 
        emails: List[str], 
        invited_by: User,
        role: str,
        message: str = None,
        organization_name: str = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Process bulk invitations with detailed tracking
        
        Args:
            emails: List of email addresses to invite
            invited_by: User sending the invitations
            role: Role to assign to invited users
            message: Optional custom message
            organization_name: Optional organization name
            
        Returns:
            dict: Contains 'successful' and 'failed' invitation lists
        """
        if not emails:
            return {
                'successful': [],
                'failed': [{'error': 'Emails list is required'}]
            }
        
        successful = []
        failed = []
        
        for email in emails:
            try:
                with transaction.atomic():
                    # Check if invitation already exists
                    if self.invitation_service.check_email_exists(email):
                        failed.append({
                            'email': email,
                            'error': 'Pending invitation already exists'
                        })
                        continue
                    
                    # Create invitation
                    invitation = Invitation.objects.create(
                        email=email,
                        role=role,
                        organization_name=organization_name or '',
                        message=message or '',
                        invited_by=invited_by
                    )
                    
                    successful.append({
                        'email': email,
                        'invitation_id': str(invitation.public_id),
                        'token': invitation.token,
                        'role': invitation.role
                    })
                    
            except Exception as e:
                failed.append({
                    'email': email,
                    'error': str(e)
                })
        
        return {
            'successful': successful,
            'failed': failed
        }
    
    def get_bulk_invitation_summary(self, result: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Generate summary statistics for bulk invitation results
        
        Args:
            result: Result from process_bulk_invitations
            
        Returns:
            dict: Summary statistics
        """
        successful_count = len(result.get('successful', []))
        failed_count = len(result.get('failed', []))
        total_count = successful_count + failed_count
        
        success_rate = 0
        if total_count > 0:
            success_rate = (successful_count / total_count) * 100
        
        return {
            'total_processed': total_count,
            'successful_count': successful_count,
            'failed_count': failed_count,
            'success_rate': round(success_rate, 2)
        }
    
    def validate_bulk_request_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate bulk invitation request data
        
        Args:
            data: Request data to validate
            
        Returns:
            dict: Validation result with errors if any
        """
        errors = []
        
        emails = data.get('emails', [])
        if not emails:
            errors.append('Emails list is required')
        elif not isinstance(emails, list):
            errors.append('Emails must be a list')
        elif len(emails) > 100:  # Reasonable limit
            errors.append('Cannot send more than 100 invitations at once')
        
        role = data.get('role', 'member')
        valid_roles = ['member', 'manager', 'admin']  # Adjust based on your role system
        if role not in valid_roles:
            errors.append(f'Invalid role. Must be one of: {", ".join(valid_roles)}')
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }