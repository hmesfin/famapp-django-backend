"""
DRF Serializers for Project Management
Ham Dog & TC's contextual serializers - different views for different crews!
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from apps.projects.models import (
    Project, ProjectMembership, Sprint, Task, Comment
)
from apps.shared.validators import DateValidators, StatusValidators

User = get_user_model()


class UserSummarySerializer(serializers.ModelSerializer):
    """Lightweight user representation for nested serialization"""
    class Meta:
        model = User
        fields = ['public_id', 'email', 'first_name', 'last_name']
        read_only_fields = fields


class ProjectMembershipSerializer(serializers.ModelSerializer):
    """Serializer for project team members"""
    user = UserSummarySerializer(read_only=True)
    user_id = serializers.UUIDField(write_only=True, required=False)
    
    class Meta:
        model = ProjectMembership
        fields = [
            'public_id', 'user', 'user_id', 'role', 'joined_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['public_id', 'joined_at', 'created_at', 'updated_at']
    
    def validate_user_id(self, value):
        """Validate user exists by public_id"""
        try:
            User.objects.get(public_id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")
        return value


class ProjectListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for project lists"""
    owner = UserSummarySerializer(read_only=True)
    member_count = serializers.SerializerMethodField()
    task_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'public_id', 'name', 'slug', 'description', 'status',
            'owner', 'member_count', 'task_count', 'start_date', 
            'end_date', 'created_at'
        ]
        read_only_fields = ['public_id', 'slug', 'created_at']
    
    def get_member_count(self, obj):
        return obj.team_members.count()
    
    def get_task_count(self, obj):
        return obj.tasks.filter(is_deleted=False).count()


class ProjectDetailSerializer(serializers.ModelSerializer):
    """Full serializer for project details"""
    owner = UserSummarySerializer(read_only=True)
    memberships = ProjectMembershipSerializer(many=True, read_only=True)
    active_sprint = serializers.SerializerMethodField()
    stats = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'public_id', 'name', 'slug', 'description', 'status',
            'owner', 'memberships', 'start_date', 'end_date',
            'active_sprint', 'stats', 'created_at', 'updated_at',
            'created_by', 'updated_by'
        ]
        read_only_fields = [
            'public_id', 'slug', 'created_at', 'updated_at',
            'created_by', 'updated_by'
        ]
    
    def get_active_sprint(self, obj):
        sprint = obj.sprints.filter(is_active=True).first()
        if sprint:
            return SprintSummarySerializer(sprint).data
        return None
    
    def get_stats(self, obj):
        tasks = obj.tasks.filter(is_deleted=False)
        return {
            'total_tasks': tasks.count(),
            'completed_tasks': tasks.filter(status='done').count(),
            'in_progress_tasks': tasks.filter(status='in_progress').count(),
            'blocked_tasks': tasks.filter(status='blocked').count(),
        }


class ProjectCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating projects"""
    owner = UserSummarySerializer(read_only=True)  # Include owner in response
    
    class Meta:
        model = Project
        fields = [
            'public_id', 'name', 'slug', 'description', 'status', 
            'start_date', 'end_date', 'owner'
        ]
        read_only_fields = ['public_id', 'slug', 'owner']
    
    def validate_name(self, value):
        """Validate project name uniqueness per owner"""
        request = self.context.get('request')
        if not request or not request.user:
            return value
        
        # Check for uniqueness
        queryset = Project.objects.filter(
            name__iexact=value,
            owner=request.user,
            is_deleted=False
        )
        
        # If updating, exclude current instance
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError(
                f'You already have a project named "{value}". Please choose a different name.'
            )
        
        return value
    
    def validate(self, attrs):
        """Validate project data"""
        # Date range validation
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        
        if start_date and end_date:
            try:
                DateValidators.validate_date_range(start_date, end_date)
            except DjangoValidationError as e:
                raise serializers.ValidationError(e.message_dict)
        
        # Status-specific validation
        status = attrs.get('status', 'planning')
        
        if status == 'active' and start_date:
            try:
                DateValidators.validate_active_project_dates(status, start_date)
            except DjangoValidationError as e:
                raise serializers.ValidationError(e.message_dict)
        
        if status == 'completed':
            try:
                StatusValidators.validate_completed_has_end_date(status, end_date)
            except DjangoValidationError as e:
                raise serializers.ValidationError(e.message_dict)
        
        # Status transition validation for updates
        if self.instance:
            old_status = self.instance.status
            new_status = attrs.get('status', old_status)
            try:
                StatusValidators.validate_status_transition(old_status, new_status)
            except DjangoValidationError as e:
                raise serializers.ValidationError(e.message_dict)
        
        return attrs
    
    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        validated_data['created_by'] = self.context['request'].user
        project = super().create(validated_data)
        # Auto-add owner as a project member
        ProjectMembership.objects.create(
            project=project,
            user=project.owner,
            role='owner'
        )
        return project


class SprintSummarySerializer(serializers.ModelSerializer):
    """Lightweight sprint serializer"""
    task_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Sprint
        fields = [
            'public_id', 'name', 'goal', 'start_date', 
            'end_date', 'is_active', 'task_count'
        ]
    
    def get_task_count(self, obj):
        return obj.tasks.filter(is_deleted=False).count()


class SprintDetailSerializer(serializers.ModelSerializer):
    """Full sprint serializer with stats"""
    project = ProjectListSerializer(read_only=True)
    stats = serializers.SerializerMethodField()
    
    class Meta:
        model = Sprint
        fields = [
            'public_id', 'project', 'name', 'goal',
            'start_date', 'end_date', 'is_active', 'stats',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['public_id', 'created_at', 'updated_at']
    
    def get_stats(self, obj):
        tasks = obj.tasks.filter(is_deleted=False)
        total_points = sum(t.story_points for t in tasks)
        completed_points = sum(
            t.story_points for t in tasks.filter(status='done')
        )
        return {
            'total_tasks': tasks.count(),
            'completed_tasks': tasks.filter(status='done').count(),
            'total_story_points': total_points,
            'completed_story_points': completed_points,
            'completion_percentage': (
                (completed_points / total_points * 100) if total_points > 0 else 0
            )
        }


class SprintCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating sprints"""
    project_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Sprint
        fields = [
            'public_id', 'project_id', 'name', 'goal',
            'start_date', 'end_date', 'is_active'
        ]
        read_only_fields = ['public_id']
    
    def validate_project_id(self, value):
        """Validate project exists and user has permission"""
        try:
            project = Project.objects.get(public_id=value)
            request = self.context.get('request')
            if request and request.user:
                # Check if user is owner or manager
                if project.owner != request.user:
                    membership = project.projectmembership_set.filter(
                        user=request.user,
                        role__in=['owner', 'manager']
                    ).first()
                    if not membership:
                        raise serializers.ValidationError(
                            "You don't have permission to manage sprints in this project"
                        )
            return project
        except Project.DoesNotExist:
            raise serializers.ValidationError("Project not found")
    
    def validate(self, attrs):
        """Validate sprint data"""
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        
        # Date range validation
        if start_date and end_date and end_date <= start_date:
            raise serializers.ValidationError({
                'end_date': 'End date must be after start date'
            })
        
        # Check for overlapping active sprints
        if attrs.get('is_active'):
            project = attrs.get('project_id')
            if project:
                active_sprints = Sprint.objects.filter(
                    project=project,
                    is_active=True
                )
                if self.instance:
                    active_sprints = active_sprints.exclude(pk=self.instance.pk)
                
                if active_sprints.exists():
                    raise serializers.ValidationError({
                        'is_active': 'Project already has an active sprint. Deactivate it first.'
                    })
        
        return attrs
    
    def create(self, validated_data):
        project = validated_data.pop('project_id')
        validated_data['project'] = project
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        if 'project_id' in validated_data:
            validated_data['project'] = validated_data.pop('project_id')
        validated_data['updated_by'] = self.context['request'].user
        return super().update(instance, validated_data)


class CommentSerializer(serializers.ModelSerializer):
    """Comment serializer with author info"""
    author = UserSummarySerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'public_id', 'content', 'author', 'parent',
            'replies', 'edited', 'created_at', 'updated_at'
        ]
        read_only_fields = ['public_id', 'edited', 'created_at', 'updated_at']
    
    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class TaskListSerializer(serializers.ModelSerializer):
    """Lightweight task serializer for lists"""
    assignee = UserSummarySerializer(read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'public_id', 'title', 'description', 'status', 'priority',
            'assignee', 'project_name', 'story_points',
            'due_date', 'created_at'
        ]
        read_only_fields = ['public_id', 'created_at']


class TaskDetailSerializer(serializers.ModelSerializer):
    """Full task serializer with all details"""
    project = ProjectListSerializer(read_only=True)
    sprint = SprintSummarySerializer(read_only=True)
    assignee = UserSummarySerializer(read_only=True)
    assignee_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    comments = CommentSerializer(many=True, read_only=True)
    created_by = UserSummarySerializer(read_only=True)
    updated_by = UserSummarySerializer(read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'public_id', 'project', 'sprint', 'title', 'description',
            'assignee', 'assignee_id', 'status', 'priority',
            'story_points', 'due_date', 'comments',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'public_id', 'created_by', 'updated_by', 
            'created_at', 'updated_at'
        ]
    
    def validate_assignee_id(self, value):
        """Validate assignee exists by public_id"""
        if value:
            try:
                User.objects.get(public_id=value)
            except User.DoesNotExist:
                raise serializers.ValidationError("Assignee not found")
        return value


class TaskCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating tasks"""
    assignee_id = serializers.UUIDField(required=False, allow_null=True)
    sprint_id = serializers.UUIDField(required=False, allow_null=True)
    
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'assignee_id', 'sprint_id',
            'status', 'priority', 'story_points', 'due_date'
        ]
    
    def validate_assignee_id(self, value):
        if value:
            try:
                return User.objects.get(public_id=value)
            except User.DoesNotExist:
                raise serializers.ValidationError("Assignee not found")
        return None
    
    def validate_sprint_id(self, value):
        if value:
            try:
                return Sprint.objects.get(public_id=value)
            except Sprint.DoesNotExist:
                raise serializers.ValidationError("Sprint not found")
        return None
    
    def create(self, validated_data):
        # Extract and convert UUID fields to model instances
        assignee = validated_data.pop('assignee_id', None)
        sprint = validated_data.pop('sprint_id', None)
        
        validated_data['assignee'] = assignee
        validated_data['sprint'] = sprint
        validated_data['created_by'] = self.context['request'].user
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # Handle UUID field conversions
        if 'assignee_id' in validated_data:
            validated_data['assignee'] = validated_data.pop('assignee_id')
        if 'sprint_id' in validated_data:
            validated_data['sprint'] = validated_data.pop('sprint_id')
        
        validated_data['updated_by'] = self.context['request'].user
        return super().update(instance, validated_data)