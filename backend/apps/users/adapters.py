from __future__ import annotations

import typing

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings

if typing.TYPE_CHECKING:
    from allauth.socialaccount.models import SocialLogin
    from django.http import HttpRequest

    from apps.users.models import User


class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request: HttpRequest) -> bool:
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)
    
    def send_mail(self, template_prefix, email, context):
        """
        Override to send HTML emails with plain text fallback.
        
        This ensures AllAuth sends beautiful HTML emails just like our
        password reset flow - because it's 2025!
        """
        from django.core.mail import EmailMultiAlternatives
        from django.template import TemplateDoesNotExist
        from django.template.loader import render_to_string
        
        # Add missing context variables for frontend URLs
        from django.contrib.sites.models import Site
        
        # Get current site info
        current_site = Site.objects.get_current()
        
        # Add protocol and domain for frontend links
        context.update({
            'protocol': 'http',  # Use https in production
            'domain': current_site.domain,
        })
        
        # Get the subject
        subject = render_to_string(f"{template_prefix}_subject.txt", context)
        subject = " ".join(subject.strip().splitlines())
        
        # Get plain text body
        body = render_to_string(f"{template_prefix}_message.txt", context)
        
        # Create email with plain text
        email_message = EmailMultiAlternatives(
            subject=subject,
            body=body,
            from_email=None,  # Use default
            to=[email]
        )
        
        # Try to attach HTML version
        try:
            html_body = render_to_string(f"{template_prefix}_message.html", context)
            email_message.attach_alternative(html_body, "text/html")
        except TemplateDoesNotExist:
            # If no HTML template exists, just send plain text
            pass
        
        email_message.send()


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(
        self,
        request: HttpRequest,
        sociallogin: SocialLogin,
    ) -> bool:
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)

    def populate_user(
        self,
        request: HttpRequest,
        sociallogin: SocialLogin,
        data: dict[str, typing.Any],
    ) -> User:
        """
        Populates user information from social provider info.

        See: https://docs.allauth.org/en/latest/socialaccount/advanced.html#creating-and-populating-user-instances
        """
        user = super().populate_user(request, sociallogin, data)
        user.first_name = data.get("first_name", "")
        user.last_name = data.get("last_name", "")
        return user
