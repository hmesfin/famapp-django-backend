"""
Email Template Service for the invitations app
Handles all email template rendering, context preparation, and preview functionality

Ham Dog & TC's Email Architecture:
- Centralized template management
- Clean separation from Celery tasks
- Support for preview functionality
- Proper error handling and logging
- Extensible for multiple email types
"""
import logging
from typing import Dict, Any, Tuple, Optional, Union
from enum import Enum
from dataclasses import dataclass
from pathlib import Path

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string, get_template
from django.template.exceptions import TemplateDoesNotExist
from django.utils import timezone
from datetime import timedelta

from apps.invitations.models import Invitation

logger = logging.getLogger(__name__)


class EmailType(Enum):
    """Email types supported by the service"""
    INVITATION = "invitation"
    REMINDER = "reminder"
    WELCOME = "welcome"
    EXPIRY_NOTICE = "expiry_notice"


@dataclass
class EmailTemplate:
    """Email template configuration"""
    html_template: str
    text_template: str
    subject_template: Optional[str] = None


@dataclass 
class EmailPreview:
    """Email preview data structure"""
    subject: str
    html_content: str
    text_content: str
    context: Dict[str, Any]
    template_paths: Dict[str, str]


class EmailTemplateService:
    """
    Service for handling email template operations
    
    Features:
    - Template rendering with context preparation
    - Preview functionality for frontend integration
    - Error handling and validation
    - Support for multiple email types
    - Configurable template paths
    """

    # Template configurations
    TEMPLATES = {
        EmailType.INVITATION: EmailTemplate(
            html_template="invitations/invitation_email.html",
            text_template="invitations/invitation_email.txt"
        ),
        EmailType.REMINDER: EmailTemplate(
            html_template="invitations/reminder_email.html", 
            text_template="invitations/reminder_email.txt"
        ),
        EmailType.WELCOME: EmailTemplate(
            html_template="invitations/welcome_email.html",
            text_template="invitations/welcome_email.txt"
        ),
        EmailType.EXPIRY_NOTICE: EmailTemplate(
            html_template="invitations/expiry_notice_email.html",
            text_template="invitations/expiry_notice_email.txt"
        )
    }

    @classmethod
    def render_invitation_email(
        cls, 
        invitation: Invitation,
        email_type: EmailType = EmailType.INVITATION,
        preview_mode: bool = False
    ) -> Union[EmailPreview, Tuple[str, str, str]]:
        """
        Render invitation email content
        
        Args:
            invitation: The invitation instance
            email_type: Type of email to render
            preview_mode: If True, return EmailPreview for frontend preview
            
        Returns:
            EmailPreview if preview_mode=True, else tuple of (subject, html, text)
            
        Raises:
            ValueError: If invitation is invalid or templates missing
            TemplateDoesNotExist: If templates are not found
        """
        try:
            # Validate invitation
            cls._validate_invitation(invitation)
            
            # Get template configuration
            template_config = cls._get_template_config(email_type)
            
            # Prepare context
            context = cls._prepare_context(invitation, email_type)
            
            # Generate subject
            subject = cls._generate_subject(invitation, email_type, context)
            
            # Render templates
            html_content = cls._render_template(template_config.html_template, context)
            text_content = cls._render_template(template_config.text_template, context)
            
            if preview_mode:
                return EmailPreview(
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content,
                    context=context,
                    template_paths={
                        'html': template_config.html_template,
                        'text': template_config.text_template
                    }
                )
            
            return subject, html_content, text_content
            
        except Exception as exc:
            invitation_id = getattr(invitation, 'id', 'unknown') if invitation else 'unknown'
            logger.error(f"Failed to render {email_type.value} email for invitation {invitation_id}: {exc}")
            raise
    
    @classmethod
    def send_invitation_email(
        cls, 
        invitation: Invitation,
        email_type: EmailType = EmailType.INVITATION,
        fail_silently: bool = False
    ) -> bool:
        """
        Render and send invitation email
        
        Args:
            invitation: The invitation instance
            email_type: Type of email to send
            fail_silently: If True, don't raise exceptions on send failure
            
        Returns:
            bool: True if email was sent successfully
            
        Raises:
            Exception: If email sending fails and fail_silently=False
        """
        try:
            # Render email content
            subject, html_content, text_content = cls.render_invitation_email(
                invitation, email_type, preview_mode=False
            )
            
            # Create email message
            email = cls._create_email_message(
                subject=subject,
                text_content=text_content,
                html_content=html_content,
                invitation=invitation
            )
            
            # Send email
            email.send(fail_silently=fail_silently)
            
            logger.info(
                f"Successfully sent {email_type.value} email to {invitation.email} "
                f"(invitation ID: {invitation.id})"
            )
            return True
            
        except Exception as exc:
            logger.error(
                f"Failed to send {email_type.value} email for invitation {invitation.id}: {exc}"
            )
            if not fail_silently:
                raise
            return False
    
    @classmethod
    def send_simple_reminder(
        cls,
        invitation: Invitation,
        fail_silently: bool = False
    ) -> bool:
        """
        Send simple reminder email (fallback for when templates don't exist)
        
        Args:
            invitation: The invitation instance
            fail_silently: If True, don't raise exceptions on send failure
            
        Returns:
            bool: True if email was sent successfully
        """
        try:
            # Calculate time remaining
            time_until_expiry = invitation.expires_at - timezone.now()
            hours_remaining = int(time_until_expiry.total_seconds() / 3600)
            
            # Build invitation URL
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
            invitation_url = f"{frontend_url}/invitations/accept?token={invitation.token}"
            
            # Generate simple content
            subject = f"⏰ Reminder: Your invitation expires in {hours_remaining} hours!"
            
            body = f"""
Hi {invitation.first_name or 'there'},

This is a friendly reminder that your invitation to join {invitation.organization_name or 'our team'} 
will expire in {hours_remaining} hours.

Click here to accept your invitation before it expires:
{invitation_url}

Best regards,
{invitation.invited_by.get_full_name() if invitation.invited_by else 'The Team'}
            """.strip()
            
            # Send simple email
            send_mail(
                subject=subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[invitation.email],
                fail_silently=fail_silently,
            )
            
            logger.info(f"Sent simple reminder for invitation {invitation.id} to {invitation.email}")
            return True
            
        except Exception as exc:
            logger.error(f"Failed to send simple reminder for invitation {invitation.id}: {exc}")
            if not fail_silently:
                raise
            return False
    
    @classmethod
    def preview_email_content(
        cls,
        invitation: Invitation,
        email_type: EmailType = EmailType.INVITATION
    ) -> EmailPreview:
        """
        Generate email preview for frontend display
        
        Args:
            invitation: The invitation instance
            email_type: Type of email to preview
            
        Returns:
            EmailPreview: Complete preview data structure
            
        Raises:
            ValueError: If invitation is invalid
            TemplateDoesNotExist: If templates are not found
        """
        return cls.render_invitation_email(
            invitation, email_type, preview_mode=True
        )
    
    @classmethod
    def get_available_templates(cls) -> Dict[str, Dict[str, str]]:
        """
        Get list of available email templates
        
        Returns:
            dict: Available templates grouped by type
        """
        templates = {}
        for email_type, template_config in cls.TEMPLATES.items():
            templates[email_type.value] = {
                'html_template': template_config.html_template,
                'text_template': template_config.text_template,
                'has_subject_template': template_config.subject_template is not None
            }
        return templates
    
    @classmethod
    def validate_templates_exist(cls) -> Dict[str, bool]:
        """
        Validate that all configured templates exist
        
        Returns:
            dict: Template existence status by email type
        """
        results = {}
        for email_type, template_config in cls.TEMPLATES.items():
            try:
                # Check HTML template
                get_template(template_config.html_template)
                html_exists = True
            except TemplateDoesNotExist:
                html_exists = False
            
            try:
                # Check text template  
                get_template(template_config.text_template)
                text_exists = True
            except TemplateDoesNotExist:
                text_exists = False
            
            results[email_type.value] = {
                'html_exists': html_exists,
                'text_exists': text_exists,
                'both_exist': html_exists and text_exists
            }
            
        return results
    
    # Private helper methods
    
    @classmethod
    def _validate_invitation(cls, invitation: Invitation) -> None:
        """Validate invitation instance"""
        if not invitation:
            raise ValueError("Invitation instance is required")
        
        if not invitation.email:
            raise ValueError("Invitation must have an email address")
            
        if invitation.status not in ['pending', 'accepted']:
            logger.warning(f"Sending email for invitation {invitation.id} with status {invitation.status}")
    
    @classmethod
    def _get_template_config(cls, email_type: EmailType) -> EmailTemplate:
        """Get template configuration for email type"""
        if email_type not in cls.TEMPLATES:
            raise ValueError(f"Unsupported email type: {email_type.value}")
        return cls.TEMPLATES[email_type]
    
    @classmethod
    def _prepare_context(cls, invitation: Invitation, email_type: EmailType) -> Dict[str, Any]:
        """Prepare template context for rendering"""
        # Build invitation URL
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
        invitation_url = f"{frontend_url}/invitations/accept?token={invitation.token}"
        
        # Prepare inviter name
        invited_by_name = ""
        if invitation.invited_by:
            invited_by_name = f"{invitation.invited_by.first_name} {invitation.invited_by.last_name}".strip()
            if not invited_by_name:
                invited_by_name = invitation.invited_by.email
        
        # Format expiration date
        expires_at_formatted = invitation.expires_at.strftime("%B %d, %Y at %I:%M %p")
        
        # Calculate days until expiry
        time_until_expiry = invitation.expires_at - timezone.now()
        expires_in_days = max(1, time_until_expiry.days)
        
        # Base context for all email types
        context = {
            'invitation': invitation,
            'invitation_url': invitation_url,
            'organization_name': invitation.organization_name,
            'expires_in_days': expires_in_days,
            'expires_at': invitation.expires_at,
            'expires_at_formatted': expires_at_formatted,
            'support_email': getattr(settings, 'SUPPORT_EMAIL', 'support@example.com'),
            'invited_by_name': invited_by_name,
            'invited_by_email': invitation.invited_by.email if invitation.invited_by else '',
            'invited_by_first_name': (invitation.invited_by.first_name if invitation.invited_by and invitation.invited_by.first_name else "your inviter"),
            'role_display': invitation.get_role_display(),
            'site_name': getattr(settings, 'SITE_NAME', 'Django Vue Starter'),
        }
        
        # Add email-type specific context
        if email_type == EmailType.REMINDER:
            hours_remaining = max(1, int(time_until_expiry.total_seconds() / 3600))
            context.update({
                'hours_remaining': hours_remaining,
                'is_reminder': True,
                'urgency_level': cls._calculate_urgency_level(time_until_expiry)
            })
        elif email_type == EmailType.WELCOME:
            context.update({
                'is_welcome': True,
                'getting_started_url': f"{frontend_url}/getting-started"
            })
        elif email_type == EmailType.EXPIRY_NOTICE:
            context.update({
                'is_expiry_notice': True,
                'expired_at': invitation.expires_at
            })
            
        return context
    
    @classmethod
    def _generate_subject(
        cls,
        invitation: Invitation,
        email_type: EmailType, 
        context: Dict[str, Any]
    ) -> str:
        """Generate email subject line"""
        org_name = invitation.organization_name or "Django Vue Starter"
        
        subject_templates = {
            EmailType.INVITATION: f"You're invited to join {org_name}!",
            EmailType.REMINDER: f"⏰ Reminder: Your {org_name} invitation expires soon!",
            EmailType.WELCOME: f"Welcome to {org_name}!",
            EmailType.EXPIRY_NOTICE: f"Your {org_name} invitation has expired"
        }
        
        # For reminder, add time-specific urgency
        if email_type == EmailType.REMINDER and 'hours_remaining' in context:
            hours = context['hours_remaining']
            if hours <= 2:
                return f"🚨 URGENT: Your {org_name} invitation expires in {hours} hour{'s' if hours != 1 else ''}!"
            else:
                return f"⏰ Reminder: Your {org_name} invitation expires in {hours} hours!"
        
        return subject_templates.get(email_type, f"Message from {org_name}")
    
    @classmethod
    def _render_template(cls, template_path: str, context: Dict[str, Any]) -> str:
        """Render template with context"""
        try:
            return render_to_string(template_path, context)
        except TemplateDoesNotExist as exc:
            logger.error(f"Template not found: {template_path}")
            raise exc
    
    @classmethod
    def _create_email_message(
        cls,
        subject: str,
        text_content: str,
        html_content: str,
        invitation: Invitation
    ) -> EmailMultiAlternatives:
        """Create EmailMultiAlternatives instance"""
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[invitation.email],
            reply_to=[invitation.invited_by.email] if invitation.invited_by else None,
        )
        
        # Attach HTML version
        email.attach_alternative(html_content, "text/html")
        
        return email
    
    @classmethod 
    def _calculate_urgency_level(cls, time_until_expiry: timedelta) -> str:
        """Calculate urgency level for reminder emails"""
        hours = time_until_expiry.total_seconds() / 3600
        
        if hours <= 3:  # Changed from 2 to 3 hours to match test expectations
            return "critical"
        elif hours <= 12:
            return "high"
        elif hours <= 24:
            return "medium"
        else:
            return "low"