"""
Project Management Models - Where the magic happens!
Ham Dog & TC's finest Django models, now properly inheriting from our shared models!
Following the NEW Commandment #1 pattern: bigint id internally, public_id for APIs!
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from apps.shared.models import BaseModel, SimpleBaseModel  # NO 'backend.' prefix!
from apps.shared.validators import DateValidators, StatusValidators, UniqueValidators

User = get_user_model()


class Project(BaseModel):
    """
    The mighty Project model - holder of all tasks and dreams!
    BaseModel provides: bigint id, public_id (UUID), timestamps, audit trail, and soft delete!
    """
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]
    
    # Basic fields
    name = models.CharField(
        max_length=255,
        help_text="The glorious name of your project"
    )
    slug = models.SlugField(
        unique=True,
        max_length=255,
        help_text="URL-friendly version of the name"
    )
    description = models.TextField(
        help_text="What's this project all about?"
    )
    
    # Relationships
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_projects',
        help_text="The big boss of this project"
    )
    team_members = models.ManyToManyField(
        User,
        through='ProjectMembership',
        related_name='member_projects',
        help_text="The crew working on this"
    )
    
    # Status and dates
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='planning',
        help_text="Current state of the project"
    )
    start_date = models.DateField(
        help_text="When the fun begins"
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="When we hope to finish (optional optimism)"
    )
    
    class Meta:
        ordering = ['-created_at']
        permissions = [
            ('can_manage_team', 'Can manage project team'),
            ('can_archive_project', 'Can archive project'),
        ]
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        # Unique constraint: one project name per owner
        constraints = [
            models.UniqueConstraint(
                fields=['owner', 'name'],
                condition=models.Q(is_deleted=False),
                name='unique_project_name_per_owner'
            )
        ]
    
    def __str__(self):
        return self.name
    
    def clean(self):
        """Validate the project before saving"""
        super().clean()
        
        # Date range validation
        if self.start_date and self.end_date:
            DateValidators.validate_date_range(self.start_date, self.end_date)
        
        # Active project date validation
        if self.status == 'active':
            DateValidators.validate_active_project_dates(self.status, self.start_date)
        
        # Completed projects must have end date
        StatusValidators.validate_completed_has_end_date(self.status, self.end_date)
        
        # Status transition validation (only for existing projects)
        if self.pk:
            try:
                old_project = Project.objects.get(pk=self.pk)
                StatusValidators.validate_status_transition(old_project.status, self.status)
            except Project.DoesNotExist:
                pass
        
        # Unique name per owner validation
        if self.owner:
            UniqueValidators.validate_unique_per_owner(
                Project, self.name, self.owner, instance=self
            )
    
    def save(self, *args, **kwargs):
        """Auto-generate slug from name if not provided"""
        # Note: Validation is handled by serializers for API calls
        # and by forms for admin. Calling full_clean() here causes
        # uncaught exceptions in the API.
        
        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while Project.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)


class ProjectMembership(SimpleBaseModel):
    """
    Through model for project team members with roles
    SimpleBaseModel provides: bigint id, public_id (UUID), and timestamps
    """
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('manager', 'Project Manager'),
        ('developer', 'Developer'),
        ('designer', 'Designer'),
        ('viewer', 'Viewer'),
    ]
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='project_memberships'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='developer'
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['project', 'user']
        ordering = ['role', 'joined_at']
        verbose_name = "Project Membership"
        verbose_name_plural = "Project Memberships"
    
    def __str__(self):
        return f"{self.user} - {self.role} on {self.project}"


class Sprint(SimpleBaseModel):
    """
    Agile sprint model for organizing work
    SimpleBaseModel provides: bigint id, public_id (UUID), and timestamps
    """
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='sprints'
    )
    name = models.CharField(
        max_length=255,
        help_text="Sprint name (e.g., 'Sprint 1', 'Alpha Release')"
    )
    goal = models.TextField(
        help_text="What are we trying to achieve this sprint?"
    )
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(
        default=False,
        help_text="Only one sprint can be active per project"
    )
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = "Sprint"
        verbose_name_plural = "Sprints"
    
    def __str__(self):
        return f"{self.project.name} - {self.name}"
    
    def save(self, *args, **kwargs):
        """Ensure only one active sprint per project"""
        if self.is_active:
            # Deactivate other sprints for this project
            Sprint.objects.filter(
                project=self.project,
                is_active=True
            ).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


class Task(BaseModel):
    """
    The Task model - where work actually gets defined!
    BaseModel provides: bigint id, public_id (UUID), timestamps, audit trail, and soft delete!
    """
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('review', 'In Review'),
        ('done', 'Done'),
        ('blocked', 'Blocked'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    # Relationships
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    sprint = models.ForeignKey(
        Sprint,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='tasks',
        help_text="Optional sprint assignment"
    )
    
    # Task details
    title = models.CharField(
        max_length=255,
        help_text="What needs to be done?"
    )
    description = models.TextField(
        help_text="Detailed description of the task"
    )
    
    # Assignment and status
    assignee = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='assigned_tasks',
        help_text="Who's working on this?"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='todo'
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium'
    )
    
    # Estimation and tracking
    story_points = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(21)],
        help_text="Story points (1-21, Fibonacci style)"
    )
    due_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When should this be done?"
    )
    
    # Note: created_by, updated_by, created_at, updated_at, is_deleted, deleted_at, deleted_by
    # are all provided by BaseModel's mixins!
    
    class Meta:
        ordering = ['priority', '-created_at']
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
    
    def __str__(self):
        return f"{self.project.name} - {self.title}"


class Comment(SimpleBaseModel):
    """
    Comments on tasks for collaboration
    SimpleBaseModel provides: bigint id, public_id (UUID), and timestamps
    """
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='task_comments'
    )
    content = models.TextField()
    
    # For threading comments (optional)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies'
    )
    
    # edited flag to track if comment was modified
    edited = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
    
    def __str__(self):
        return f"Comment by {self.author} on {self.task.title}"
    
    def save(self, *args, **kwargs):
        """Mark as edited if updating existing comment"""
        if self.pk and self.content:
            self.edited = True
        super().save(*args, **kwargs)