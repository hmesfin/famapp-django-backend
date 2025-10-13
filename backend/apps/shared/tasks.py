"""
Celery tasks for FamApp background job processing.

Tasks include:
- Todo reminders (email notifications before due date)
- Event reminders (email notifications before event start)
- Pet care reminders (daily feeding/walking notifications)
- Daily digest emails (summary of family activities)
- Cleanup tasks (old soft-deleted records)

Ham Dog & TC building async magic! 🔮
"""

import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from apps.shared.models import GroceryItem
from apps.shared.models import Pet
from apps.shared.models import PetActivity
from apps.shared.models import ScheduleEvent
from apps.shared.models import Todo

logger = logging.getLogger(__name__)


# ============================================================================
# Todo Reminder Tasks
# ============================================================================


@shared_task
def send_todo_reminders(lead_time_hours=1):
    """
    Send email reminders for todos that are due soon.

    Args:
        lead_time_hours: Hours before due date to send reminder (default: 1)

    Returns:
        dict: Count of reminders sent
    """
    cutoff_time = timezone.now() + timedelta(hours=lead_time_hours)

    # Find todos that are due within lead time and not completed
    upcoming_todos = Todo.objects.filter(
        due_date__lte=cutoff_time,
        due_date__gte=timezone.now(),
        status__in=[Todo.Status.TODO, Todo.Status.IN_PROGRESS],
        is_deleted=False,
    )

    reminder_count = 0
    for todo in upcoming_todos:
        # TODO: Send actual email via SendGrid
        # For now, just log
        logger.info(
            f"TODO REMINDER: {todo.title} due at {todo.due_date} "
            f"(family: {todo.family.name})"
        )
        reminder_count += 1

    return {"reminders_sent": reminder_count, "lead_time_hours": lead_time_hours}


# ============================================================================
# Event Reminder Tasks
# ============================================================================


@shared_task
def send_event_reminders(lead_time_minutes=15):
    """
    Send email reminders for events starting soon.

    Args:
        lead_time_minutes: Minutes before event to send reminder (default: 15)

    Returns:
        dict: Count of reminders sent
    """
    cutoff_time = timezone.now() + timedelta(minutes=lead_time_minutes)

    # Find events starting within lead time
    upcoming_events = ScheduleEvent.objects.filter(
        start_time__lte=cutoff_time,
        start_time__gte=timezone.now(),
        is_deleted=False,
    )

    reminder_count = 0
    for event in upcoming_events:
        # TODO: Send actual email via SendGrid
        # For now, just log
        logger.info(
            f"EVENT REMINDER: {event.title} starts at {event.start_time} "
            f"(family: {event.family.name})"
        )
        reminder_count += 1

    return {"reminders_sent": reminder_count, "lead_time_minutes": lead_time_minutes}


# ============================================================================
# Pet Care Reminder Tasks
# ============================================================================


@shared_task
def send_pet_feeding_reminders():
    """
    Send reminders for pets that need feeding today.

    Checks PetActivity records to see which pets haven't been fed today.

    Returns:
        dict: Count of reminders sent
    """
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

    # Get all active pets
    pets = Pet.objects.filter(is_deleted=False)

    reminder_count = 0
    for pet in pets:
        # Check if pet has been fed today
        fed_today = PetActivity.objects.filter(
            pet=pet,
            activity_type=PetActivity.ActivityType.FEEDING,
            is_completed=True,
            completed_at__gte=today_start,
        ).exists()

        if not fed_today:
            # TODO: Send actual SMS/email via Twilio/SendGrid
            # For now, just log
            logger.info(
                f"PET FEEDING REMINDER: {pet.name} needs feeding "
                f"(family: {pet.family.name})"
            )
            reminder_count += 1

    return {"reminders_sent": reminder_count}


@shared_task
def send_pet_walking_reminders():
    """
    Send reminders for pets that need walking today.

    Checks PetActivity records to see which pets haven't been walked today.

    Returns:
        dict: Count of reminders sent
    """
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

    # Get all active pets (dogs only for walking)
    pets = Pet.objects.filter(
        species=Pet.Species.DOG,
        is_deleted=False,
    )

    reminder_count = 0
    for pet in pets:
        # Check if pet has been walked today
        walked_today = PetActivity.objects.filter(
            pet=pet,
            activity_type=PetActivity.ActivityType.WALKING,
            is_completed=True,
            completed_at__gte=today_start,
        ).exists()

        if not walked_today:
            # TODO: Send actual SMS/email via Twilio/SendGrid
            # For now, just log
            logger.info(
                f"PET WALKING REMINDER: {pet.name} needs walking "
                f"(family: {pet.family.name})"
            )
            reminder_count += 1

    return {"reminders_sent": reminder_count}


# ============================================================================
# Cleanup Tasks
# ============================================================================


@shared_task
def cleanup_old_soft_deleted_records(days_old=30):
    """
    Hard delete soft-deleted records older than specified days.

    Args:
        days_old: Days since soft delete to permanently delete (default: 30)

    Returns:
        dict: Count of records deleted by model
    """
    cutoff_date = timezone.now() - timedelta(days=days_old)

    deleted_counts = {}

    # Cleanup old todos
    deleted_counts["todos"] = Todo.objects.filter(
        is_deleted=True,
        deleted_at__lte=cutoff_date,
    ).delete()[0]

    # Cleanup old events
    deleted_counts["events"] = ScheduleEvent.objects.filter(
        is_deleted=True,
        deleted_at__lte=cutoff_date,
    ).delete()[0]

    # Cleanup old grocery items
    deleted_counts["groceries"] = GroceryItem.objects.filter(
        is_deleted=True,
        deleted_at__lte=cutoff_date,
    ).delete()[0]

    # Cleanup old pets
    deleted_counts["pets"] = Pet.objects.filter(
        is_deleted=True,
        deleted_at__lte=cutoff_date,
    ).delete()[0]

    logger.info(f"Cleanup complete: {deleted_counts}")

    return deleted_counts


# ============================================================================
# Daily Digest Tasks
# ============================================================================


@shared_task
def send_daily_digest():
    """
    Send daily digest email to families summarizing today's activities.

    Includes:
    - Upcoming todos due today
    - Events scheduled for today
    - Pet care activities completed today

    Returns:
        dict: Count of digests sent
    """
    # TODO: Implement daily digest logic
    # For now, just log
    logger.info("Daily digest task executed (not yet implemented)")
    return {"digests_sent": 0, "status": "stub"}
