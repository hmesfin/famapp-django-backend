"""
Shared validators for the entire application.
DRY validation logic that can be reused across models and serializers.
"""

from datetime import date, datetime
from typing import Optional
from django.core.exceptions import ValidationError
from django.utils import timezone


class DateValidators:
    """Date-related validation utilities"""

    @staticmethod
    def validate_date_range(start_date: date, end_date: Optional[date]) -> None:
        """Validate that start_date is before end_date"""
        if end_date and start_date > end_date:
            raise ValidationError(
                {
                    "end_date": "🤔 Unless you have a time machine, projects can't end before they start! Move that end date forward, friend!"
                }
            )

    @staticmethod
    def validate_not_in_past(date_value: date, field_name: str = "date") -> None:
        """Validate that a date is not in the past"""
        if date_value < timezone.now().date():
            raise ValidationError(
                {
                    field_name: f"{field_name.replace('_', ' ').title()} cannot be in the past."
                }
            )

    @staticmethod
    def validate_active_project_dates(status: str, start_date: date) -> None:
        """Validate that active projects don't start in the past"""
        if status == "active" and start_date < timezone.now().date():
            raise ValidationError(
                {
                    "start_date": '⏰ Whoa there, time traveler! Active projects can\'t start yesterday. Either move that date forward or switch to "Planning" status while you build your DeLorean!'
                }
            )


class StatusValidators:
    """Status transition validation utilities"""

    # Define allowed status transitions
    ALLOWED_TRANSITIONS = {
        "planning": ["active", "on_hold", "archived"],
        "active": ["on_hold", "completed", "archived"],
        "on_hold": ["active", "planning", "archived"],
        "completed": ["archived"],
        "archived": [],  # No transitions from archived
    }

    @classmethod
    def validate_status_transition(cls, old_status: str, new_status: str) -> None:
        """Validate that a status transition is allowed"""
        if old_status == new_status:
            return  # No transition

        allowed = cls.ALLOWED_TRANSITIONS.get(old_status, [])
        if new_status not in allowed:
            # More friendly messages for common mistakes
            if old_status == "completed" and new_status in ["planning", "active"]:
                message = "🏁 Nice try! But completed projects are DONE! They can't un-complete themselves. You can archive it, or start a fresh new project!"
            elif old_status == "archived":
                message = "📦 This project is in the archives vault! It's like trying to un-send an email - not happening! Time to create a shiny new project instead!"
            else:
                friendly_allowed = (
                    ", ".join(allowed)
                    if allowed
                    else "absolutely nothing (it's stuck!)"
                )
                message = f'🚦 Oops! Can\'t go from "{old_status}" to "{new_status}". Your options from here: {friendly_allowed}'

            raise ValidationError({"status": message})

    @staticmethod
    def validate_completed_has_end_date(status: str, end_date: Optional[date]) -> None:
        """Validate that completed projects have an end date"""
        if status == "completed" and not end_date:
            raise ValidationError(
                {
                    "end_date": "🎯 Hold up! You marked this as completed but didn't say when! Even miracles have end dates. Pick one!"
                }
            )


class UniqueValidators:
    """Uniqueness validation utilities"""

    @staticmethod
    def validate_unique_per_owner(model_class, name: str, owner, instance=None):
        """Validate that a name is unique per owner"""
        queryset = model_class.objects.filter(
            name__iexact=name,  # Case-insensitive comparison
            owner=owner,
            is_deleted=False,
        )

        # Exclude current instance if updating
        if instance and instance.pk:
            queryset = queryset.exclude(pk=instance.pk)

        if queryset.exists():
            # Fun messages for duplicate names
            fun_suggestions = [
                f'"{name} 2: Electric Boogaloo"',
                f'"{name} Returns"',
                f'"{name}: The Sequel"',
                f'"Son of {name}"',
                f'"{name} Reloaded"',
            ]
            import random

            suggestion = random.choice(fun_suggestions)

            raise ValidationError(
                {
                    "name": f'🎬 Déjà vu! You already have a project called "{name}"! How about {suggestion}? Or, you know, something actually original? 😉'
                }
            )
