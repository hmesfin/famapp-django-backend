"""
Shared abstract models for the DjVue Orchestra
Ham Dog & TC's foundation for all Django models

Following the Ten Commandments:
- Commandment #1: UUIDs instead of bigint IDs (civilized coding!)
- Commandment #7: DRY principles for the salvation of our sanity
"""

import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone


class UUIDMixin(models.Model):
    """
    Abstract model that provides public UUID for external APIs while keeping bigint id as PK.

    The Stripe/Instagram Pattern:
    - `id`: bigint primary key (fast joins, indexes, internal operations)
    - `public_id`: UUID for external APIs, URLs, and public references
    - `uuid`: Legacy field (will be removed after migration)

    Commandment #1 Updated: "Use semantic naming - `id` for DB, `public_id` for APIs!"
    """

    # NEW: The public-facing UUID identifier (not a primary key!)
    public_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text="Public UUID for external API references and URLs",
    )

    # LEGACY: Keep old uuid field during migration (will be removed later)
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        help_text="Legacy UUID field - will be removed after migration to public_id",
    )

    class Meta:
        abstract = True


class TimestampedMixin(models.Model):
    """
    Abstract model that provides created_at and updated_at fields.

    Because every model needs to know when it was born and when it last changed!
    """

    created_at = models.DateTimeField(
        auto_now_add=True, help_text="When this record was first created"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="When this record was last updated"
    )

    class Meta:
        abstract = True
        ordering = ["-created_at"]  # Newest first by default


class AuditMixin(models.Model):
    """
    Abstract model that provides audit trail fields.

    Tracks who created and who last modified a record.
    Perfect for accountability and debugging!
    """

    created_by = models.ForeignKey(
        "users.User",  # Use string reference to avoid circular imports
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created",
        help_text="User who created this record",
    )
    updated_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_updated",
        help_text="User who last updated this record",
    )

    class Meta:
        abstract = True


class SoftDeleteMixin(models.Model):
    """
    Abstract model that provides soft delete functionality.

    Instead of actually deleting records, we mark them as deleted.
    This allows for data recovery and audit trails.
    """

    is_deleted = models.BooleanField(
        default=False,
        db_index=True,  # Index for performance on queries
        help_text="Soft delete flag - if True, record is considered deleted",
    )
    deleted_at = models.DateTimeField(
        null=True, blank=True, help_text="When this record was soft deleted"
    )
    deleted_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_deleted",
        help_text="User who soft deleted this record",
    )

    class Meta:
        abstract = True

    def soft_delete(self, user=None):
        """
        Soft delete this instance.

        Args:
            user: User who is performing the deletion (optional)
        """
        self.is_deleted = True
        self.deleted_at = timezone.now()
        if user:
            self.deleted_by = user
        self.save(update_fields=["is_deleted", "deleted_at", "deleted_by"])

    def restore(self):
        """
        Restore a soft deleted instance.
        """
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.save(update_fields=["is_deleted", "deleted_at", "deleted_by"])

    @property
    def is_active(self):
        """
        Check if record is active (not soft deleted).
        """
        return not self.is_deleted


class BaseModel(UUIDMixin, TimestampedMixin, AuditMixin, SoftDeleteMixin):
    """
    The ultimate base model that combines all our mixins.

    Use this when you want the full Ham Dog & TC experience:
    - UUID primary keys (Commandment #1)
    - Timestamp tracking
    - Audit trails
    - Soft delete capability

    Perfect for important business models!
    """

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def __str__(self):
        """
        Default string representation using UUID.
        Override in subclasses for better representation.
        """
        return f"{self.__class__.__name__}({str(self.id)[:8]}...)"


class SimpleBaseModel(UUIDMixin, TimestampedMixin):
    """
    A lighter base model with just UUID and timestamps.

    Use this for simpler models that don't need audit trails or soft deletes.
    Still follows Commandment #1 with UUID primary keys!
    """

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def __str__(self):
        """
        Default string representation using UUID.
        Override in subclasses for better representation.
        """
        return f"{self.__class__.__name__}({str(self.id)[:8]}...)"


# ============================================================================
# FamApp Models
# ============================================================================


class Family(BaseModel):
    """
    Family model for FamApp.

    Represents a family unit that can collaborate on todos, schedules,
    grocery lists, and pet care.
    """

    name = models.CharField(max_length=100, help_text="Family name")

    # ManyToMany relationship with User through FamilyMember
    members = models.ManyToManyField(
        "users.User", through="FamilyMember", related_name="families"
    )

    class Meta:
        verbose_name = "Family"
        verbose_name_plural = "Families"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class FamilyMember(SimpleBaseModel):
    """
    FamilyMember model - through table for Family <-> User relationship.

    Tracks the role of each user in a family (ORGANIZER, PARENT, CHILD).
    Uses SimpleBaseModel (no audit trail, no soft delete) for simplicity.
    """

    class Role(models.TextChoices):
        ORGANIZER = "organizer", "Organizer"
        PARENT = "parent", "Parent"
        CHILD = "child", "Child"

    family = models.ForeignKey(
        Family, on_delete=models.CASCADE, help_text="Family this member belongs to"
    )
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, help_text="User who is a family member"
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.PARENT,
        help_text="Role of the user in this family",
    )

    class Meta:
        unique_together = ("family", "user")
        verbose_name = "Family Member"
        verbose_name_plural = "Family Members"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} - {self.family.name} ({self.get_role_display()})"


class Todo(BaseModel):
    """
    Todo model for FamApp.

    Represents a todo item that belongs to a family and can be assigned to a user.
    Tracks status, priority, and due date for task management.
    """

    class Status(models.TextChoices):
        TODO = "todo", "To Do"
        IN_PROGRESS = "in_progress", "In Progress"
        DONE = "done", "Done"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    title = models.CharField(max_length=200, help_text="Todo title")
    description = models.TextField(blank=True, help_text="Todo description")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TODO,
        help_text="Todo status",
    )
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        help_text="Todo priority",
    )
    due_date = models.DateTimeField(
        null=True, blank=True, help_text="Due date for the todo"
    )
    assigned_to = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="todo_assigned_to",
        help_text="User assigned to this todo",
    )
    family = models.ForeignKey(
        Family, on_delete=models.CASCADE, help_text="Family this todo belongs to"
    )

    class Meta:
        verbose_name = "Todo"
        verbose_name_plural = "Todos"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.family.name})"


class ScheduleEvent(BaseModel):
    """
    ScheduleEvent model for FamApp.

    Represents a calendar/schedule event that belongs to a family and can be assigned to a user.
    Tracks event type, start/end times, and location for event management.
    """

    class EventType(models.TextChoices):
        APPOINTMENT = "appointment", "Appointment"
        MEETING = "meeting", "Meeting"
        REMINDER = "reminder", "Reminder"
        OTHER = "other", "Other"

    title = models.CharField(max_length=200, help_text="Event title")
    description = models.TextField(blank=True, help_text="Event description")
    event_type = models.CharField(
        max_length=20,
        choices=EventType.choices,
        default=EventType.OTHER,
        help_text="Type of event",
    )
    start_time = models.DateTimeField(help_text="Event start time")
    end_time = models.DateTimeField(help_text="Event end time")
    location = models.CharField(max_length=255, blank=True, help_text="Event location")
    assigned_to = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="scheduleevent_assigned_to",
        help_text="User assigned to this event",
    )
    family = models.ForeignKey(
        Family, on_delete=models.CASCADE, help_text="Family this event belongs to"
    )

    class Meta:
        verbose_name = "Schedule Event"
        verbose_name_plural = "Schedule Events"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.family.name})"


class GroceryItem(BaseModel):
    """
    GroceryItem model for FamApp.

    Represents a grocery list item that belongs to a family.
    Tracks quantity, unit, category, and purchase status for shopping management.
    """

    class Category(models.TextChoices):
        PRODUCE = "produce", "Produce"
        DAIRY = "dairy", "Dairy"
        MEAT = "meat", "Meat"
        BAKERY = "bakery", "Bakery"
        PANTRY = "pantry", "Pantry"
        FROZEN = "frozen", "Frozen"
        OTHER = "other", "Other"

    name = models.CharField(max_length=200, help_text="Item name")
    quantity = models.IntegerField(default=1, help_text="Quantity to purchase")
    unit = models.CharField(
        max_length=50, blank=True, help_text="Unit of measurement (e.g., lbs, dozen)"
    )
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.OTHER,
        help_text="Grocery category",
    )
    is_purchased = models.BooleanField(
        default=False, help_text="Whether the item has been purchased"
    )
    added_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="groceryitem_added_by",
        help_text="User who added this item",
    )
    family = models.ForeignKey(
        Family, on_delete=models.CASCADE, help_text="Family this item belongs to"
    )

    class Meta:
        verbose_name = "Grocery Item"
        verbose_name_plural = "Grocery Items"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.family.name})"


class Pet(BaseModel):
    """
    Pet model for FamApp.

    Represents a family pet.
    Tracks species, breed, age, and notes for pet management.
    """

    class Species(models.TextChoices):
        DOG = "dog", "Dog"
        CAT = "cat", "Cat"
        BIRD = "bird", "Bird"
        FISH = "fish", "Fish"
        OTHER = "other", "Other"

    name = models.CharField(max_length=100, help_text="Pet name")
    species = models.CharField(
        max_length=20,
        choices=Species.choices,
        default=Species.OTHER,
        help_text="Pet species",
    )
    breed = models.CharField(max_length=100, blank=True, help_text="Pet breed")
    age = models.IntegerField(null=True, blank=True, help_text="Pet age in years")
    notes = models.TextField(blank=True, help_text="Additional pet notes")
    family = models.ForeignKey(
        Family, on_delete=models.CASCADE, help_text="Family this pet belongs to"
    )

    class Meta:
        verbose_name = "Pet"
        verbose_name_plural = "Pets"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.family.name})"


class PetActivity(BaseModel):
    """
    PetActivity model for FamApp.

    Represents a scheduled activity for a pet (feeding, walking, vet visit, etc.).
    Tracks activity type, scheduled time, completion status, and notes.
    """

    class ActivityType(models.TextChoices):
        FEEDING = "feeding", "Feeding"
        WALKING = "walking", "Walking"
        GROOMING = "grooming", "Grooming"
        VET_VISIT = "vet_visit", "Vet Visit"
        MEDICATION = "medication", "Medication"
        PLAYTIME = "playtime", "Playtime"
        OTHER = "other", "Other"

    activity_type = models.CharField(
        max_length=20,
        choices=ActivityType.choices,
        help_text="Type of pet activity",
    )
    scheduled_time = models.DateTimeField(help_text="When this activity is scheduled")
    notes = models.TextField(blank=True, help_text="Activity notes")
    is_completed = models.BooleanField(
        default=False, help_text="Whether the activity has been completed"
    )
    completed_at = models.DateTimeField(
        null=True, blank=True, help_text="When this activity was completed"
    )
    completed_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="petactivity_completed_by",
        help_text="User who completed this activity",
    )
    pet = models.ForeignKey(
        Pet, on_delete=models.CASCADE, help_text="Pet this activity is for"
    )

    class Meta:
        verbose_name = "Pet Activity"
        verbose_name_plural = "Pet Activities"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_activity_type_display()} - {self.pet.name}"
