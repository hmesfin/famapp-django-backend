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
