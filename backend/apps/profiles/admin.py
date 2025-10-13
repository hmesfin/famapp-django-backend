"""
Django Admin configuration for Profile and UserSettings models
Ham Dog & TC's admin interface excellence!
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from apps.profiles.models import Profile, UserSettings


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Admin interface for Profile model.
    Provides comprehensive management with search, filtering, and inline editing.
    """
    
    # List display configuration
    list_display = [
        'user_email',
        'user_full_name',
        'location',
        'company',
        'profile_completion',
        'avatar_preview',
        'created_at',
        'is_active_badge'
    ]
    
    # List filters
    list_filter = [
        'created_at',
        'updated_at',
        'is_deleted',
        'user__is_active',
        'user__is_staff'
    ]
    
    # Search configuration
    search_fields = [
        'user__email',
        'user__first_name',
        'user__last_name',
        'bio',
        'location',
        'company',
        'public_id'
    ]
    
    # Readonly fields
    readonly_fields = [
        'public_id',
        'uuid',  # Legacy UUID field
        'created_at',
        'updated_at',
        'created_by',
        'updated_by',
        'deleted_at',
        'deleted_by',
        'avatar_preview_large'
    ]
    
    # Field organization
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'public_id')
        }),
        ('Profile Details', {
            'fields': ('bio', 'location', 'company', 'website', 'avatar_url', 'avatar_preview_large')
        }),
        ('Audit Trail', {
            'fields': ('created_at', 'created_by', 'updated_at', 'updated_by'),
            'classes': ('collapse',)
        }),
        ('Soft Delete', {
            'fields': ('is_deleted', 'deleted_at', 'deleted_by'),
            'classes': ('collapse',)
        }),
        ('Legacy Fields', {
            'fields': ('uuid',),
            'classes': ('collapse',),
            'description': 'Legacy UUID field - will be removed in future migration'
        })
    )
    
    # Ordering
    ordering = ['-created_at']
    
    # Items per page
    list_per_page = 25
    
    # Enable date hierarchy navigation
    date_hierarchy = 'created_at'
    
    # Custom admin methods
    def user_email(self, obj):
        """Display user email with link to user admin"""
        if obj.user:
            url = reverse('admin:users_user_change', args=[obj.user.pk])
            return format_html('<a href="{}">{}</a>', url, obj.user.email)
        return '-'
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'
    
    def user_full_name(self, obj):
        """Display user's full name"""
        if obj.user:
            full_name = f"{obj.user.first_name} {obj.user.last_name}".strip()
            return full_name if full_name else '-'
        return '-'
    user_full_name.short_description = 'Full Name'
    
    def profile_completion(self, obj):
        """Calculate and display profile completion percentage"""
        fields = ['bio', 'location', 'company', 'website', 'avatar_url']
        filled = sum(1 for field in fields if getattr(obj, field))
        percentage = (filled / len(fields)) * 100
        
        # Color coding based on completion
        if percentage >= 80:
            color = 'green'
        elif percentage >= 50:
            color = 'orange'
        else:
            color = 'red'
        
        # Format percentage first, then pass to format_html
        percentage_str = '{:.0f}%'.format(percentage)
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            percentage_str
        )
    profile_completion.short_description = 'Completion'
    
    def avatar_preview(self, obj):
        """Show avatar thumbnail in list view"""
        if obj.avatar_url:
            return format_html(
                '<img src="{}" width="30" height="30" style="border-radius: 50%;" />',
                obj.avatar_url
            )
        return format_html(
            '<div style="width: 30px; height: 30px; background: #ddd; border-radius: 50%; display: inline-block;"></div>'
        )
    avatar_preview.short_description = 'Avatar'
    
    def avatar_preview_large(self, obj):
        """Show larger avatar preview in detail view"""
        if obj.avatar_url:
            return format_html(
                '<img src="{}" width="100" height="100" style="border-radius: 10px;" />',
                obj.avatar_url
            )
        return 'No avatar set'
    avatar_preview_large.short_description = 'Avatar Preview'
    
    def is_active_badge(self, obj):
        """Display active status as a badge"""
        if obj.is_active:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 3px;">Active</span>'
            )
        return format_html(
            '<span style="background: #dc3545; color: white; padding: 3px 8px; border-radius: 3px;">Deleted</span>'
        )
    is_active_badge.short_description = 'Status'
    
    # Custom actions
    def soft_delete_profiles(self, request, queryset):
        """Soft delete selected profiles"""
        count = 0
        for profile in queryset:
            if not profile.is_deleted:
                profile.soft_delete(user=request.user)
                count += 1
        self.message_user(request, '{} profile(s) soft deleted.'.format(count))
    soft_delete_profiles.short_description = 'Soft delete selected profiles'
    
    def restore_profiles(self, request, queryset):
        """Restore soft deleted profiles"""
        count = 0
        for profile in queryset:
            if profile.is_deleted:
                profile.restore()
                count += 1
        self.message_user(request, '{} profile(s) restored.'.format(count))
    restore_profiles.short_description = 'Restore selected profiles'
    
    actions = ['soft_delete_profiles', 'restore_profiles']


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    """
    Admin interface for UserSettings model.
    Manages user preferences and settings with advanced filtering.
    """
    
    # List display
    list_display = [
        'user_email',
        'theme_badge',
        'language',
        'timezone',
        'notification_status',
        'visibility_badge',
        'created_at'
    ]
    
    # List filters
    list_filter = [
        'theme',
        'language',
        'profile_visibility',
        'email_notifications',
        'push_notifications',
        'show_email',
        'show_activity',
        'created_at'
    ]
    
    # Search
    search_fields = [
        'user__email',
        'user__first_name',
        'user__last_name',
        'timezone',
        'public_id'
    ]
    
    # Readonly fields
    readonly_fields = [
        'public_id',
        'uuid',  # Legacy field
        'created_at',
        'updated_at',
        'metadata_preview'
    ]
    
    # Field organization
    fieldsets = (
        ('User', {
            'fields': ('user', 'public_id')
        }),
        ('Display Preferences', {
            'fields': ('theme', 'language', 'timezone')
        }),
        ('Notification Settings', {
            'fields': ('email_notifications', 'push_notifications')
        }),
        ('Privacy Settings', {
            'fields': ('profile_visibility', 'show_email', 'show_activity')
        }),
        ('Metadata', {
            'fields': ('metadata', 'metadata_preview'),
            'classes': ('collapse',),
            'description': 'JSON field for storing additional user preferences'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Legacy Fields', {
            'fields': ('uuid',),
            'classes': ('collapse',),
            'description': 'Legacy UUID field - will be removed in future migration'
        })
    )
    
    # Ordering
    ordering = ['-created_at']
    
    # Items per page
    list_per_page = 25
    
    # Custom admin methods
    def user_email(self, obj):
        """Display user email with link"""
        if obj.user:
            url = reverse('admin:users_user_change', args=[obj.user.pk])
            return format_html('<a href="{}">{}</a>', url, obj.user.email)
        return '-'
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'
    
    def theme_badge(self, obj):
        """Display theme as a colored badge"""
        colors = {
            'light': '#f8f9fa',
            'dark': '#343a40',
            'auto': '#6c757d'
        }
        text_colors = {
            'light': '#000',
            'dark': '#fff',
            'auto': '#fff'
        }
        return format_html(
            '<span style="background: {}; color: {}; padding: 3px 8px; border-radius: 3px;">{}</span>',
            colors.get(obj.theme, '#6c757d'),
            text_colors.get(obj.theme, '#fff'),
            obj.get_theme_display()
        )
    theme_badge.short_description = 'Theme'
    
    def notification_status(self, obj):
        """Display notification settings summary"""
        icons = []
        if obj.email_notifications:
            icons.append('📧')
        if obj.push_notifications:
            icons.append('🔔')
        
        if not icons:
            return format_html('<span style="color: #999;">None</span>')
        return ' '.join(icons)
    notification_status.short_description = 'Notifications'
    
    def visibility_badge(self, obj):
        """Display visibility setting as badge"""
        colors = {
            'public': '#28a745',
            'private': '#dc3545',
            'friends': '#ffc107'
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            colors.get(obj.profile_visibility, '#6c757d'),
            obj.get_profile_visibility_display()
        )
    visibility_badge.short_description = 'Visibility'
    
    def metadata_preview(self, obj):
        """Display formatted metadata"""
        if obj.metadata:
            import json
            formatted = json.dumps(obj.metadata, indent=2)
            return format_html('<pre style="font-size: 11px;">{}</pre>', formatted)
        return 'No metadata'
    metadata_preview.short_description = 'Metadata Preview'
    
    # Custom actions
    def reset_to_defaults(self, request, queryset):
        """Reset selected settings to defaults"""
        count = queryset.update(
            theme='light',
            language='en',
            timezone='UTC',
            email_notifications=True,
            push_notifications=False,
            profile_visibility='public',
            show_email=False,
            show_activity=True
        )
        self.message_user(request, '{} settings reset to defaults.'.format(count))
    reset_to_defaults.short_description = 'Reset to default settings'
    
    def enable_all_notifications(self, request, queryset):
        """Enable all notifications for selected users"""
        count = queryset.update(
            email_notifications=True,
            push_notifications=True
        )
        self.message_user(request, 'Enabled all notifications for {} user(s).'.format(count))
    enable_all_notifications.short_description = 'Enable all notifications'
    
    def disable_all_notifications(self, request, queryset):
        """Disable all notifications for selected users"""
        count = queryset.update(
            email_notifications=False,
            push_notifications=False
        )
        self.message_user(request, 'Disabled all notifications for {} user(s).'.format(count))
    disable_all_notifications.short_description = 'Disable all notifications'
    
    actions = ['reset_to_defaults', 'enable_all_notifications', 'disable_all_notifications']