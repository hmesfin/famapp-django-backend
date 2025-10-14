"""
Django admin configuration for shared app models.
"""

from django.contrib import admin

from apps.shared.models import Family
from apps.shared.models import FamilyMember
from apps.shared.models import GroceryItem
from apps.shared.models import Pet
from apps.shared.models import PetActivity
from apps.shared.models import ScheduleEvent
from apps.shared.models import Todo


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    """Admin interface for Family model."""

    list_display = ("name", "created_at", "updated_at", "is_deleted")
    list_filter = ("created_at", "updated_at", "is_deleted")
    search_fields = ("name", "public_id")  # Enable autocomplete
    readonly_fields = ("public_id", "created_at", "updated_at", "created_by", "updated_by")
    date_hierarchy = "created_at"


@admin.register(FamilyMember)
class FamilyMemberAdmin(admin.ModelAdmin):
    """Admin interface for FamilyMember model."""

    list_display = ("user", "family", "role", "created_at")
    list_filter = ("role", "created_at")
    search_fields = ("user__email", "user__first_name", "user__last_name", "family__name")
    readonly_fields = ("public_id", "created_at", "updated_at")
    autocomplete_fields = ("user", "family")


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    """Admin interface for Todo model."""

    list_display = ("title", "family", "status", "priority", "due_date", "assigned_to", "is_deleted")
    list_filter = ("status", "priority", "created_at", "due_date", "is_deleted")
    search_fields = ("title", "description", "family__name")
    readonly_fields = ("public_id", "created_at", "updated_at", "created_by", "updated_by")
    autocomplete_fields = ("family", "assigned_to")
    date_hierarchy = "due_date"


@admin.register(ScheduleEvent)
class ScheduleEventAdmin(admin.ModelAdmin):
    """Admin interface for ScheduleEvent model."""

    list_display = ("title", "family", "event_type", "start_time", "end_time", "location", "is_deleted")
    list_filter = ("event_type", "start_time", "created_at", "is_deleted")
    search_fields = ("title", "description", "location", "family__name")
    readonly_fields = ("public_id", "created_at", "updated_at", "created_by", "updated_by")
    autocomplete_fields = ("family", "assigned_to")
    date_hierarchy = "start_time"


@admin.register(GroceryItem)
class GroceryItemAdmin(admin.ModelAdmin):
    """Admin interface for GroceryItem model."""

    list_display = ("name", "family", "quantity", "unit", "category", "is_purchased", "is_deleted")
    list_filter = ("is_purchased", "category", "created_at", "is_deleted")
    search_fields = ("name", "family__name")
    readonly_fields = ("public_id", "created_at", "updated_at", "created_by", "updated_by")
    autocomplete_fields = ("family", "added_by")


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    """Admin interface for Pet model."""

    list_display = ("name", "family", "species", "breed", "age", "is_deleted")
    list_filter = ("species", "created_at", "is_deleted")
    search_fields = ("name", "breed", "family__name", "notes")
    readonly_fields = ("public_id", "created_at", "updated_at", "created_by", "updated_by")
    autocomplete_fields = ("family",)


@admin.register(PetActivity)
class PetActivityAdmin(admin.ModelAdmin):
    """Admin interface for PetActivity model."""

    list_display = ("pet", "activity_type", "scheduled_time", "is_completed", "completed_by", "is_deleted")
    list_filter = ("activity_type", "is_completed", "scheduled_time", "is_deleted")
    search_fields = ("pet__name", "notes")
    readonly_fields = ("public_id", "created_at", "updated_at", "created_by", "updated_by")
    autocomplete_fields = ("pet", "completed_by")
    date_hierarchy = "scheduled_time"
