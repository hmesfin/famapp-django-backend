"""
Django Admin configuration for Project Management
Ham Dog & TC's admin interface for managing projects like pros!
"""
from django.contrib import admin
from django.utils.html import format_html
from apps.projects.models import (
    Project, ProjectMembership, Sprint, Task, Comment
)


class ProjectMembershipInline(admin.TabularInline):
    """Inline admin for project team members"""
    model = ProjectMembership
    extra = 1
    fields = ['user', 'role', 'joined_at']
    readonly_fields = ['joined_at']
    autocomplete_fields = ['user']


class SprintInline(admin.TabularInline):
    """Inline admin for project sprints"""
    model = Sprint
    extra = 0
    fields = ['name', 'start_date', 'end_date', 'is_active']
    show_change_link = True


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin interface for Projects"""
    list_display = [
        'name', 'status', 'owner', 'member_count', 
        'task_count', 'start_date', 'created_at'
    ]
    list_filter = ['status', 'created_at', 'start_date']
    search_fields = ['name', 'description', 'owner__username', 'owner__email']
    readonly_fields = [
        'public_id', 'uuid', 'slug', 'created_at', 'updated_at',
        'created_by', 'updated_by', 'deleted_at', 'deleted_by'
    ]
    autocomplete_fields = ['owner']
    inlines = [ProjectMembershipInline, SprintInline]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'status')
        }),
        ('Ownership & Team', {
            'fields': ('owner',)
        }),
        ('Timeline', {
            'fields': ('start_date', 'end_date')
        }),
        ('System Fields', {
            'classes': ('collapse',),
            'fields': (
                'public_id', 'uuid', 'created_at', 'updated_at',
                'created_by', 'updated_by', 'is_deleted', 'deleted_at', 'deleted_by'
            )
        }),
    )
    
    def member_count(self, obj):
        """Display number of team members"""
        count = obj.team_members.count()
        return format_html('<b>{}</b> members', count)
    member_count.short_description = 'Team Size'
    
    def task_count(self, obj):
        """Display number of tasks"""
        count = obj.tasks.filter(is_deleted=False).count()
        return format_html('<b>{}</b> tasks', count)
    task_count.short_description = 'Tasks'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related and prefetch_related"""
        qs = super().get_queryset(request)
        return qs.select_related('owner').prefetch_related('team_members', 'tasks')


@admin.register(Sprint)
class SprintAdmin(admin.ModelAdmin):
    """Admin interface for Sprints"""
    list_display = [
        'name', 'project', 'start_date', 'end_date', 
        'is_active', 'task_count', 'created_at'
    ]
    list_filter = ['is_active', 'start_date', 'end_date', 'project']
    search_fields = ['name', 'goal', 'project__name']
    readonly_fields = ['public_id', 'uuid', 'created_at', 'updated_at']
    autocomplete_fields = ['project']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Sprint Information', {
            'fields': ('project', 'name', 'goal')
        }),
        ('Timeline', {
            'fields': ('start_date', 'end_date', 'is_active')
        }),
        ('System Fields', {
            'classes': ('collapse',),
            'fields': ('public_id', 'uuid', 'created_at', 'updated_at')
        }),
    )
    
    def task_count(self, obj):
        """Display number of tasks in sprint"""
        count = obj.tasks.filter(is_deleted=False).count()
        return format_html('<b>{}</b> tasks', count)
    task_count.short_description = 'Tasks'
    
    actions = ['activate_sprints', 'deactivate_sprints']
    
    def activate_sprints(self, request, queryset):
        """Activate selected sprints"""
        for sprint in queryset:
            sprint.is_active = True
            sprint.save()
        self.message_user(request, f"{queryset.count()} sprints activated.")
    activate_sprints.short_description = "Activate selected sprints"
    
    def deactivate_sprints(self, request, queryset):
        """Deactivate selected sprints"""
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} sprints deactivated.")
    deactivate_sprints.short_description = "Deactivate selected sprints"


class CommentInline(admin.TabularInline):
    """Inline admin for task comments"""
    model = Comment
    extra = 0
    fields = ['author', 'content', 'created_at']
    readonly_fields = ['created_at']
    autocomplete_fields = ['author']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin interface for Tasks"""
    list_display = [
        'title', 'project', 'status', 'priority', 
        'assignee', 'story_points', 'due_date', 'created_at'
    ]
    list_filter = ['status', 'priority', 'project', 'sprint', 'created_at']
    search_fields = ['title', 'description', 'project__name', 'assignee__username']
    readonly_fields = [
        'public_id', 'uuid', 'created_at', 'updated_at',
        'created_by', 'updated_by', 'deleted_at', 'deleted_by'
    ]
    autocomplete_fields = ['project', 'sprint', 'assignee']
    inlines = [CommentInline]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Task Information', {
            'fields': ('project', 'sprint', 'title', 'description')
        }),
        ('Assignment & Status', {
            'fields': ('assignee', 'status', 'priority', 'story_points', 'due_date')
        }),
        ('System Fields', {
            'classes': ('collapse',),
            'fields': (
                'public_id', 'uuid', 'created_at', 'updated_at',
                'created_by', 'updated_by', 'is_deleted', 'deleted_at', 'deleted_by'
            )
        }),
    )
    
    actions = ['mark_as_done', 'mark_as_in_progress', 'soft_delete_tasks']
    
    def mark_as_done(self, request, queryset):
        """Mark selected tasks as done"""
        queryset.update(status='done', updated_by=request.user)
        self.message_user(request, f"{queryset.count()} tasks marked as done.")
    mark_as_done.short_description = "Mark selected tasks as done"
    
    def mark_as_in_progress(self, request, queryset):
        """Mark selected tasks as in progress"""
        queryset.update(status='in_progress', updated_by=request.user)
        self.message_user(request, f"{queryset.count()} tasks marked as in progress.")
    mark_as_in_progress.short_description = "Mark selected tasks as in progress"
    
    def soft_delete_tasks(self, request, queryset):
        """Soft delete selected tasks"""
        for task in queryset:
            task.soft_delete(user=request.user)
        self.message_user(request, f"{queryset.count()} tasks soft deleted.")
    soft_delete_tasks.short_description = "Soft delete selected tasks"
    
    def get_queryset(self, request):
        """Show only non-deleted tasks by default"""
        qs = super().get_queryset(request)
        return qs.filter(is_deleted=False).select_related(
            'project', 'sprint', 'assignee', 'created_by', 'updated_by'
        )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin interface for Comments"""
    list_display = [
        'get_comment_preview', 'author', 'task', 
        'edited', 'created_at'
    ]
    list_filter = ['edited', 'created_at']
    search_fields = ['content', 'author__username', 'task__title']
    readonly_fields = ['public_id', 'uuid', 'created_at', 'updated_at', 'edited']
    autocomplete_fields = ['task', 'author', 'parent']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Comment Information', {
            'fields': ('task', 'author', 'content', 'parent')
        }),
        ('Metadata', {
            'fields': ('edited', 'created_at', 'updated_at')
        }),
        ('System Fields', {
            'classes': ('collapse',),
            'fields': ('public_id', 'uuid')
        }),
    )
    
    def get_comment_preview(self, obj):
        """Show preview of comment content"""
        preview = obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
        return format_html('<em>{}</em>', preview)
    get_comment_preview.short_description = 'Comment'
    
    def get_queryset(self, request):
        """Optimize queryset"""
        qs = super().get_queryset(request)
        return qs.select_related('task', 'author', 'parent')


@admin.register(ProjectMembership)
class ProjectMembershipAdmin(admin.ModelAdmin):
    """Admin interface for Project Memberships"""
    list_display = ['user', 'project', 'role', 'joined_at']
    list_filter = ['role', 'joined_at']
    search_fields = ['user__username', 'user__email', 'project__name']
    readonly_fields = ['public_id', 'uuid', 'joined_at', 'created_at', 'updated_at']
    autocomplete_fields = ['project', 'user']
    date_hierarchy = 'joined_at'
    
    def get_queryset(self, request):
        """Optimize queryset"""
        qs = super().get_queryset(request)
        return qs.select_related('project', 'user')