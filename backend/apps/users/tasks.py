import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

from .models import Invitation, User

logger = logging.getLogger(__name__)


@shared_task()
def get_users_count():
    """A pointless Celery task to demonstrate usage."""
    return User.objects.count()


@shared_task(bind=True, max_retries=3)
def send_invitation_email(self, invitation_id):
    """
    Send invitation email to invitee with accept/decline links.

    Args:
        invitation_id: ID of the Invitation model instance

    Retries: 3 times with exponential backoff on failure
    """
    try:
        # Fetch invitation with related objects
        invitation = Invitation.objects.select_related('inviter', 'family').get(id=invitation_id)

        # Build email context
        context = {
            'inviter_name': invitation.inviter.get_full_name() or invitation.inviter.email,
            'family_name': invitation.family.name,
            'role': invitation.get_role_display(),  # Human-readable role
            'invitation_token': str(invitation.token),
            'expires_at': invitation.expires_at,
            'invitee_email': invitation.invitee_email,
        }

        # Build accept/decline URLs (frontend URLs - configurable via settings)
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
        context['accept_url'] = f"{frontend_url}/invitations/{invitation.token}/accept"
        context['decline_url'] = f"{frontend_url}/invitations/{invitation.token}/decline"

        # Send email using Django's send_mail
        subject = f"You're invited to join {invitation.family.name} on FamApp!"

        # Render HTML email template
        html_message = render_to_string('emails/invitation.html', context)
        text_message = render_to_string('emails/invitation.txt', context)

        send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[invitation.invitee_email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Invitation email sent successfully to {invitation.invitee_email} (invitation_id={invitation_id})")
        return {"status": "success", "invitation_id": invitation_id}

    except Invitation.DoesNotExist:
        logger.error(f"Invitation with id={invitation_id} does not exist")
        return {"status": "error", "message": "Invitation not found"}

    except Exception as exc:
        logger.error(f"Failed to send invitation email (invitation_id={invitation_id}): {exc}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task
def cleanup_expired_invitations():
    """
    Daily task to mark expired PENDING invitations as EXPIRED.

    Runs daily at 2 AM UTC to clean up invitations that have passed
    their expiration date but are still in PENDING status.

    Returns:
        dict: Summary of cleanup operation including count and timestamp
    """
    # Find expired PENDING invitations
    expired_invitations = Invitation.objects.filter(
        status=Invitation.Status.PENDING,
        expires_at__lt=timezone.now()
    )

    count = expired_invitations.count()

    if count > 0:
        # Update status to EXPIRED using bulk update for efficiency
        updated = expired_invitations.update(
            status=Invitation.Status.EXPIRED
        )

        logger.info(
            f"Marked {updated} expired invitation(s) as EXPIRED "
            f"(expired before {timezone.now()})"
        )

        return {
            "status": "success",
            "expired_count": updated,
            "timestamp": timezone.now().isoformat()
        }
    else:
        logger.info("No expired invitations found to cleanup")
        return {
            "status": "success",
            "expired_count": 0,
            "timestamp": timezone.now().isoformat()
        }
