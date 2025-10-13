"""
Authentication utility functions.
Ham Dog & TC's helper functions for auth flows.

Reusable functions for email verification and other auth tasks.
"""
from django.core.signing import Signer
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.sites.models import Site
import logging

logger = logging.getLogger(__name__)


def send_verification_email(user):
    """
    Send verification email to a user.
    
    Args:
        user: User instance to send verification email to
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Create signed verification token
        signer = Signer()
        verification_token = signer.sign(f"email_verify_{user.pk}_{user.email}")
        
        # Prepare email context using Django Sites
        current_site = Site.objects.get_current()
        
        context = {
            'user': user,
            'verification_url': f"http://{current_site.domain}/auth/verify-email?token={verification_token}",
            'site_name': current_site.name,
        }
        
        # Render email templates
        subject = 'Django Vue Starter - Verify Your Email Address'
        html_message = render_to_string('emails/verify_email.html', context)
        plain_message = render_to_string('emails/verify_email.txt', context)
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Verification email sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send verification email to {user.email}: {e}")
        return False