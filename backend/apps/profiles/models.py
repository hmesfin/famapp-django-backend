"""
Profile and UserSettings models
Ham Dog & TC's user profile goodness! 🚀

Following the Ten Commandments:
- Commandment #1: Using UUID (public_id) for external APIs
- Commandment #7: DRY principles with shared base models
"""
from django.contrib.auth import get_user_model
from django.db import models
from apps.shared.models import BaseModel, SimpleBaseModel

User = get_user_model()


class Profile(BaseModel):
    """
    User profile model with extended information.
    
    Uses BaseModel for full audit trail and soft delete capabilities.
    One-to-one relationship with User model.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        help_text="The user this profile belongs to"
    )
    
    bio = models.TextField(
        blank=True,
        default="",
        help_text="User's biography or description"
    )
    
    location = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="User's location"
    )
    
    website = models.URLField(
        blank=True,
        default="",
        help_text="User's personal website"
    )
    
    company = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="User's company or organization"
    )
    
    avatar_url = models.URLField(
        blank=True,
        default="",
        help_text="URL to user's avatar image"
    )
    
    class Meta:
        db_table = "profiles"
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"Profile for {self.user.email}"


class UserSettings(SimpleBaseModel):
    """
    User settings and preferences model.
    
    Uses SimpleBaseModel since settings don't need audit trail or soft delete.
    One-to-one relationship with User model.
    """
    THEME_CHOICES = [
        ("light", "Light"),
        ("dark", "Dark"),
        ("auto", "Auto"),
    ]
    
    VISIBILITY_CHOICES = [
        ("public", "Public"),
        ("private", "Private"),
        ("friends", "Friends Only"),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='settings',
        help_text="The user these settings belong to"
    )
    
    # Notification preferences
    email_notifications = models.BooleanField(
        default=True,
        help_text="Receive email notifications"
    )
    
    push_notifications = models.BooleanField(
        default=False,
        help_text="Receive push notifications"
    )
    
    # Display preferences
    theme = models.CharField(
        max_length=10,
        choices=THEME_CHOICES,
        default="light",
        help_text="UI theme preference"
    )
    
    language = models.CharField(
        max_length=10,
        default="en",
        help_text="Preferred language code"
    )
    
    timezone = models.CharField(
        max_length=50,
        default="UTC",
        help_text="User's timezone"
    )
    
    # Privacy settings
    profile_visibility = models.CharField(
        max_length=10,
        choices=VISIBILITY_CHOICES,
        default="public",
        help_text="Profile visibility setting"
    )
    
    show_email = models.BooleanField(
        default=False,
        help_text="Show email address on public profile"
    )
    
    show_activity = models.BooleanField(
        default=True,
        help_text="Show activity on public profile"
    )
    
    # Flexible metadata storage for future settings
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional settings metadata"
    )
    
    class Meta:
        db_table = "user_settings"
        verbose_name = "User Settings"
        verbose_name_plural = "User Settings"
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"Settings for {self.user.email}"