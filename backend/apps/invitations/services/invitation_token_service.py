"""
Invitation Token Service
Handles token generation, validation, and regeneration logic for invitations

Ham Dog's Django Commandments:
- Keep services stateless
- Pass all dependencies explicitly
- Return structured data, not domain objects
- Secure token generation with proper entropy
"""

import secrets
from datetime import timedelta
from typing import Dict, Optional

from django.utils import timezone
from django.db import transaction

from apps.invitations.models import Invitation


class InvitationTokenService:
    """
    Service for managing invitation tokens
    
    Handles:
    - Secure token generation
    - Token uniqueness validation
    - Token expiry calculations
    - Token regeneration for resends
    """
    
    # Token configuration
    TOKEN_LENGTH = 48  # URL-safe base64 encoded
    DEFAULT_EXPIRY_DAYS = 7
    
    def generate_unique_token(self) -> str:
        """
        Generate a cryptographically secure unique token
        
        Returns:
            str: URL-safe unique token
            
        Raises:
            RuntimeError: If unable to generate unique token after max attempts
        """
        max_attempts = 100  # Prevent infinite loop in edge cases
        
        for attempt in range(max_attempts):
            token = secrets.token_urlsafe(self.TOKEN_LENGTH)
            if not self._token_exists(token):
                return token
        
        # This should never happen with proper entropy
        raise RuntimeError("Unable to generate unique token after maximum attempts")
    
    def _token_exists(self, token: str) -> bool:
        """
        Check if a token already exists in the database
        
        Args:
            token: Token to check for existence
            
        Returns:
            bool: True if token exists
        """
        return Invitation.objects.filter(token=token).exists()
    
    def calculate_expiry_date(self, days: int = None) -> timezone.datetime:
        """
        Calculate expiry date for invitation token
        
        Args:
            days: Number of days from now for expiry (default: 7)
            
        Returns:
            datetime: Expiry datetime
        """
        if days is None:
            days = self.DEFAULT_EXPIRY_DAYS
            
        return timezone.now() + timedelta(days=days)
    
    def is_token_expired(self, expires_at: Optional[timezone.datetime]) -> bool:
        """
        Check if a token has expired
        
        Args:
            expires_at: Expiry datetime to check
            
        Returns:
            bool: True if expired or no expiry date
        """
        if not expires_at:
            return False
            
        return timezone.now() > expires_at
    
    def validate_token(self, token: str) -> Dict:
        """
        Validate an invitation token and return validation status
        Optimized with select_related to avoid N+1 queries
        
        Args:
            token: Token to validate
            
        Returns:
            dict: Validation result with status and details
        """
        try:
            invitation = Invitation.objects.select_related('invited_by').get(token=token)
        except Invitation.DoesNotExist:
            return {
                'is_valid': False,
                'error': 'invalid_token',
                'message': 'Invalid invitation token',
                'invitation': None
            }
        
        # Check if invitation is soft-deleted
        if invitation.is_deleted:
            return {
                'is_valid': False,
                'error': 'deleted_invitation',
                'message': 'Invitation has been deleted',
                'invitation': invitation
            }
        
        # Check expiry
        is_expired = self.is_token_expired(invitation.expires_at)
        
        # Check status
        is_pending = invitation.status == 'pending'
        
        # Token is valid if not expired and still pending
        is_valid = not is_expired and is_pending
        
        result = {
            'is_valid': is_valid,
            'invitation': invitation,
            'is_expired': is_expired,
            'is_pending': is_pending
        }
        
        # Add specific error details if invalid
        if not is_valid:
            if is_expired:
                result['error'] = 'expired_token'
                result['message'] = 'Token has expired'
            elif not is_pending:
                result['error'] = 'invalid_status'
                result['message'] = f'Invitation status is {invitation.status}'
        
        return result
    
    @transaction.atomic
    def regenerate_token(self, invitation: Invitation, expiry_days: int = None) -> Dict:
        """
        Generate a new token for an existing invitation
        
        Args:
            invitation: Invitation to regenerate token for
            expiry_days: Number of days for new expiry (default: 7)
            
        Returns:
            dict: Result with new token details
        """
        if invitation.is_deleted:
            return {
                'success': False,
                'error': 'deleted_invitation',
                'message': 'Cannot regenerate token for deleted invitation'
            }
        
        # Generate new token and expiry
        new_token = self.generate_unique_token()
        new_expiry = self.calculate_expiry_date(expiry_days)
        
        # Store old token for logging/audit purposes
        old_token = invitation.token
        
        # Update invitation with new token
        invitation.token = new_token
        invitation.expires_at = new_expiry
        
        # Reset status to pending if it was expired/cancelled
        if invitation.status in ['expired', 'cancelled']:
            invitation.status = 'pending'
            
        invitation.save()
        
        return {
            'success': True,
            'old_token': old_token,
            'new_token': new_token,
            'expires_at': new_expiry,
            'invitation': invitation
        }
    
    def get_token_info(self, token: str) -> Dict:
        """
        Get comprehensive information about a token
        Optimized to use already fetched invitation data
        
        Args:
            token: Token to get information for
            
        Returns:
            dict: Token information and status
        """
        validation = self.validate_token(token)  # This now uses select_related
        
        if not validation['invitation']:
            return validation
        
        invitation = validation['invitation']
        
        # Calculate time remaining
        time_remaining = None
        if invitation.expires_at and not validation['is_expired']:
            time_remaining = invitation.expires_at - timezone.now()
        
        # Access invited_by safely since it's now prefetched
        invited_by_email = None
        if invitation.invited_by:
            invited_by_email = invitation.invited_by.email
        
        return {
            **validation,
            'token_info': {
                'created_at': invitation.created_at,
                'expires_at': invitation.expires_at,
                'time_remaining': time_remaining,
                'status': invitation.status,
                'email': invitation.email,
                'invited_by': invited_by_email
            }
        }