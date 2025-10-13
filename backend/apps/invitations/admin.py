"""
Django Admin configuration for Invitations
Ham Dog & TC's invitation management system!
TDD-driven and admin-friendly 🎉
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.urls import reverse
from django.utils.safestring import mark_safe

from apps.invitations.models import Invitation


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    """Admin interface for managing invitations"""

    list_display = [
        'email',
        'first_name',
        'last_name',
        'get_status_display',
        'role',
        'organization_name',
        'invited_by',
        'get_expiry_status',
        'created_at',
        'get_quick_actions'
    ]

    list_filter = [
        'status',
        'role',
        'is_deleted',
        'created_at',
        'expires_at'
    ]

    search_fields = [
        'email',
        'organization_name',
        'invited_by__email',
        'invited_by__username',
        'accepted_by__email',
        'token'
    ]

    readonly_fields = [
        'public_id',
        'uuid',
        'token',
        'get_invitation_link',
        'is_expired',
        'accepted_by',
        'accepted_at',
        'created_at',
        'updated_at',
        'created_by',
        'updated_by',
        'deleted_at',
        'deleted_by'
    ]

    autocomplete_fields = ['invited_by']
    
    # Optimize list view queries to avoid N+1 problems
    list_select_related = ['invited_by', 'accepted_by']

    date_hierarchy = 'created_at'

    fieldsets = (
        ('Invitation Details', {
            'fields': (
                'email',
                'first_name',
                'last_name',
                'status',
                'role',
                'organization_name',
                'message'
            )
        }),
        ('Invitation Link', {
            'fields': ('get_invitation_link', 'token'),
            'description': 'Share this link with the invitee'
        }),
        ('Sender Information', {
            'fields': ('invited_by',)
        }),
        ('Acceptance Information', {
            'fields': ('accepted_by', 'accepted_at'),
            'classes': ('collapse',)
        }),
        ('Expiry Information', {
            'fields': ('expires_at', 'is_expired')
        }),
        ('System Fields', {
            'classes': ('collapse',),
            'fields': (
                'public_id',
                'uuid',
                'created_at',
                'updated_at',
                'created_by',
                'updated_by',
                'is_deleted',
                'deleted_at',
                'deleted_by'
            )
        }),
    )

    actions = [
        'resend_invitations',
        'cancel_invitations',
        'extend_expiry_7_days',
        'soft_delete_invitations'
    ]

    def get_status_display(self, obj):
        """Display status with color coding"""
        colors = {
            'pending': '#FFA500',  # Orange
            'accepted': '#008000',  # Green
            'expired': '#808080',  # Gray
            'cancelled': '#FF0000',  # Red
        }
        color = colors.get(obj.status, '#000000')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    get_status_display.short_description = 'Status'
    get_status_display.admin_order_field = 'status'

    def get_expiry_status(self, obj):
        """Show expiry status with visual indicator"""
        if not obj or not obj.pk:
            return '-'  # New unsaved invitation

        if obj.status == 'accepted':
            return format_html('<span style="color: green;">✓ Accepted</span>')
        elif obj.status == 'cancelled':
            return format_html('<span style="color: red;">✗ Cancelled</span>')
        elif obj.is_expired:
            return format_html('<span style="color: red;">⏰ Expired</span>')
        elif obj.expires_at:
            days_left = (obj.expires_at - timezone.now()).days
            if days_left <= 1:
                color = 'red'
                emoji = '⚠️'
            elif days_left <= 3:
                color = 'orange'
                emoji = '⏳'
            else:
                color = 'green'
                emoji = '✓'
            return format_html(
                '<span style="color: {};">{} {} days left</span>',
                color, emoji, days_left
            )
        else:
            return '-'
    get_expiry_status.short_description = 'Expiry'

    def get_invitation_link(self, obj):
        """Generate clickable invitation link"""
        if obj and obj.pk and obj.token:
            # In production, this would be your frontend URL
            base_url = 'http://localhost:5173'  # Vue frontend URL
            link = f'{base_url}/invitations/accept?token={obj.token}'
            return format_html(
                '<a href="{}" target="_blank" style="color: #0066cc; text-decoration: underline;">📧 Copy Invitation Link</a>',
                link
            )
        return '-'
    get_invitation_link.short_description = 'Invitation Link'

    def get_quick_actions(self, obj):
        """Show available actions based on status"""
        # Check if obj is actually an Invitation instance (not the request)
        if not hasattr(obj, 'status'):
            return '-'

        actions = []

        if obj.status == 'pending' and not obj.is_expired:
            actions.append(
                format_html(
                    '<a href="#" onclick="alert(\'Use the Resend action from the dropdown\'); return false;" '
                    'style="color: #0066cc; margin-right: 10px;">↻ Resend</a>'
                )
            )

        if obj.status in ['pending', 'expired']:
            actions.append(
                format_html(
                    '<a href="#" onclick="alert(\'Use the Cancel action from the dropdown\'); return false;" '
                    'style="color: #cc0000;">✗ Cancel</a>'
                )
            )

        return mark_safe(' '.join(actions)) if actions else '-'
    get_quick_actions.short_description = 'Quick Actions'

    def resend_invitations(self, request, queryset):
        """Resend selected invitations with new tokens"""
        resent_count = 0
        skipped_count = 0

        for invitation in queryset:
            if invitation.status == 'pending':
                invitation.resend()
                resent_count += 1
            else:
                skipped_count += 1

        if resent_count:
            self.message_user(
                request,
                f"✅ Successfully resent {resent_count} invitation(s)."
            )
        if skipped_count:
            self.message_user(
                request,
                f"⚠️ Skipped {skipped_count} invitation(s) (not in pending status).",
                level='WARNING'
            )
    resend_invitations.short_description = "↻ Resend selected invitations"

    def cancel_invitations(self, request, queryset):
        """Cancel selected invitations"""
        cancelled_count = 0
        skipped_count = 0

        for invitation in queryset:
            if invitation.status in ['pending', 'expired']:
                invitation.cancel()
                cancelled_count += 1
            else:
                skipped_count += 1

        if cancelled_count:
            self.message_user(
                request,
                f"✅ Successfully cancelled {cancelled_count} invitation(s)."
            )
        if skipped_count:
            self.message_user(
                request,
                f"⚠️ Skipped {skipped_count} invitation(s) (already accepted or cancelled).",
                level='WARNING'
            )
    cancel_invitations.short_description = "✗ Cancel selected invitations"

    def extend_expiry_7_days(self, request, queryset):
        """Extend expiry by 7 days for selected invitations"""
        from datetime import timedelta

        extended_count = 0
        skipped_count = 0

        for invitation in queryset:
            if invitation.status == 'pending':
                invitation.expires_at = timezone.now() + timedelta(days=7)
                invitation.save()
                extended_count += 1
            else:
                skipped_count += 1

        if extended_count:
            self.message_user(
                request,
                f"✅ Extended expiry for {extended_count} invitation(s) by 7 days."
            )
        if skipped_count:
            self.message_user(
                request,
                f"⚠️ Skipped {skipped_count} invitation(s) (not in pending status).",
                level='WARNING'
            )
    extend_expiry_7_days.short_description = "📅 Extend expiry by 7 days"

    def soft_delete_invitations(self, request, queryset):
        """Soft delete selected invitations"""
        for invitation in queryset:
            invitation.soft_delete(user=request.user)

        self.message_user(
            request,
            f"🗑️ Soft deleted {queryset.count()} invitation(s)."
        )
    soft_delete_invitations.short_description = "🗑️ Soft delete selected invitations"

    def get_queryset(self, request):
        """
        Optimize queryset with select_related for all foreign keys
        Show all invitations including soft-deleted by default
        Enhanced optimization to prevent N+1 queries
        """
        qs = super().get_queryset(request)
        return qs.select_related(
            'invited_by',
            'accepted_by', 
            'created_by',
            'updated_by',
            'deleted_by'
        ).order_by('-created_at')  # Consistent ordering for performance

    def has_delete_permission(self, request, obj=None):
        """
        Override to prevent hard delete from admin
        Users should use soft delete action instead
        """
        return False  # Prevent hard delete, use soft delete action

    class Media:
        css = {
            'all': ('admin/css/invitation_admin.css',)
        }
