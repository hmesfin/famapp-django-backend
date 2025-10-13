"""
Celery tasks for the invitations app
Ham Dog & TC doing it the RIGHT way - async all the things!

Refactored to use EmailTemplateService for clean separation of concerns:
- Tasks handle async/retry logic
- Service handles template rendering and email composition
"""

import logging

from celery import shared_task
from django.utils import timezone

from apps.invitations.services.email_template_service import (
    EmailTemplateService,
    EmailType,
)

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_invitation_email(self, invitation_id: int) -> bool:
    """
    Send invitation email to the invited user

    Args:
        invitation_id: The ID of the invitation to send

    Returns:
        bool: True if email was sent successfully

    Retries:
        3 times with exponential backoff
    """
    from apps.invitations.models import Invitation

    try:
        invitation = Invitation.objects.select_related("invited_by").get(
            id=invitation_id
        )
    except Invitation.DoesNotExist:
        logger.error(f"Invitation {invitation_id} not found")
        return False

    # Check if invitation is still valid
    if invitation.status != "pending":
        logger.warning(
            f"Invitation {invitation_id} is not pending (status: {invitation.status})"
        )
        return False

    if invitation.is_expired:
        logger.warning(f"Invitation {invitation_id} has expired")
        return False

    try:
        # Use EmailTemplateService to handle all template logic
        success = EmailTemplateService.send_invitation_email(
            invitation=invitation, email_type=EmailType.INVITATION, fail_silently=False
        )

        if success:
            logger.info(
                f"Successfully sent invitation email to {invitation.email} (ID: {invitation_id})"
            )
        else:
            logger.error(
                f"EmailTemplateService failed to send invitation email {invitation_id}"
            )

        return success

    except Exception as exc:
        logger.error(f"Failed to send invitation email {invitation_id}: {str(exc)}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2**self.request.retries))


@shared_task(bind=True, max_retries=3)
def send_invitation_reminder(self, invitation_id: int) -> bool:
    """
    Send a reminder email for pending invitations about to expire

    Args:
        invitation_id: The ID of the invitation to remind about

    Returns:
        bool: True if reminder was sent successfully
    """
    from apps.invitations.models import Invitation
    from datetime import timedelta

    try:
        invitation = Invitation.objects.select_related("invited_by").get(
            id=invitation_id
        )
    except Invitation.DoesNotExist:
        logger.error(f"Invitation {invitation_id} not found")
        return False

    # Check if invitation needs a reminder
    if invitation.status != "pending":
        return False

    if invitation.is_expired:
        return False

    # Check if expiring soon (within 2 days)
    time_until_expiry = invitation.expires_at - timezone.now()
    if time_until_expiry > timedelta(days=2):
        logger.info(f"Invitation {invitation_id} not expiring soon, skipping reminder")
        return False

    try:
        # Try to send reminder using templates first, fall back to simple email
        try:
            success = EmailTemplateService.send_invitation_email(
                invitation=invitation,
                email_type=EmailType.REMINDER,
                fail_silently=False,
            )
        except Exception as template_exc:
            logger.warning(
                f"Template reminder failed for invitation {invitation_id}: {template_exc}"
            )
            logger.info(
                f"Falling back to simple reminder for invitation {invitation_id}"
            )

            # Fallback to simple reminder
            success = EmailTemplateService.send_simple_reminder(
                invitation=invitation, fail_silently=False
            )

        if success:
            logger.info(
                f"Successfully sent reminder for invitation {invitation_id} to {invitation.email}"
            )
        else:
            logger.error(f"Failed to send reminder for invitation {invitation_id}")

        return success

    except Exception as exc:
        logger.error(f"Failed to send invitation reminder {invitation_id}: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (2**self.request.retries))


@shared_task
def check_and_expire_invitations() -> int:
    """
    Periodic task to check and mark expired invitations
    Should be run daily via Celery Beat

    Returns:
        int: Number of invitations marked as expired
    """
    from apps.invitations.models import Invitation

    # Find all pending invitations that have expired
    expired_invitations = Invitation.objects.filter(
        status="pending", expires_at__lt=timezone.now()
    )

    count = expired_invitations.update(status="expired")

    if count > 0:
        logger.info(f"Marked {count} invitations as expired")

    return count


@shared_task
def send_pending_invitation_reminders() -> int:
    """
    Periodic task to send reminders for invitations about to expire
    Should be run daily via Celery Beat

    Returns:
        int: Number of reminders sent
    """
    from apps.invitations.models import Invitation
    from datetime import timedelta

    # Find invitations expiring in the next 48 hours
    expiring_soon = timezone.now() + timedelta(days=2)

    invitations_to_remind = Invitation.objects.filter(
        status="pending",
        expires_at__lte=expiring_soon,
        expires_at__gt=timezone.now(),
    )

    reminders_sent = 0
    for invitation in invitations_to_remind:
        # Queue reminder task
        send_invitation_reminder.delay(invitation.id)
        reminders_sent += 1

    if reminders_sent > 0:
        logger.info(f"Queued {reminders_sent} invitation reminders")

    return reminders_sent


@shared_task
def cleanup_old_invitations(days_old: int = 30) -> int:
    """
    Clean up old expired/cancelled invitations

    Args:
        days_old: Delete invitations older than this many days (default 30)

    Returns:
        int: Number of invitations deleted
    """
    from apps.invitations.models import Invitation
    from datetime import timedelta

    cutoff_date = timezone.now() - timedelta(days=days_old)

    # Soft delete old expired/cancelled invitations
    old_invitations = Invitation.objects.filter(
        status__in=["expired", "cancelled"], updated_at__lt=cutoff_date
    )

    count = old_invitations.count()

    # Perform soft delete
    for invitation in old_invitations:
        invitation.delete()  # This triggers soft delete

    if count > 0:
        logger.info(f"Cleaned up {count} old invitations")

    return count
