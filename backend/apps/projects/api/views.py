"""
API ViewSets for Project Management
Ham Dog & TC's RESTful endpoints with proper RBAC
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()

from apps.projects.models import (
    Project, ProjectMembership, Sprint, Task, Comment
)
from apps.projects.api.serializers import (
    ProjectListSerializer, ProjectDetailSerializer, ProjectCreateUpdateSerializer,
    ProjectMembershipSerializer, SprintSummarySerializer, SprintDetailSerializer,
    SprintCreateUpdateSerializer, TaskListSerializer, TaskDetailSerializer, 
    TaskCreateUpdateSerializer, CommentSerializer
)
from apps.projects.permissions import (
    IsProjectOwner, IsProjectMember, IsProjectManagerOrOwner,
    IsTaskAssigneeOrManager, IsCommentAuthorOrManager, CanManageProjectTeam
)


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Project CRUD operations
    Provides list, create, retrieve, update, and destroy actions
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'updated_at', 'start_date', 'status']
    ordering = ['-created_at']
    lookup_field = 'public_id'
    
    def get_queryset(self):
        """Filter projects where user is owner or member"""
        user = self.request.user
        return Project.objects.filter(
            Q(owner=user) | Q(team_members=user)
        ).distinct().select_related('owner').prefetch_related('team_members')
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'list':
            return ProjectListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProjectCreateUpdateSerializer
        return ProjectDetailSerializer
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsProjectOwner()]
        elif self.action in ['retrieve']:
            return [IsAuthenticated(), IsProjectMember()]
        return [IsAuthenticated()]
    
    def create(self, request, *args, **kwargs):
        """Create a new project with proper error handling"""
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError as e:
            # Handle unique constraint violations
            if 'unique_project_name_per_owner' in str(e):
                raise ValidationError({
                    'name': f'You already have a project named "{request.data.get("name", "")}". Please choose a different name.'
                })
            # Re-raise other integrity errors
            raise ValidationError({'detail': 'Unable to create project. Please check your data and try again.'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsProjectManagerOrOwner])
    def add_member(self, request, public_id=None):
        """Add a team member to the project"""
        project = self.get_object()
        serializer = ProjectMembershipSerializer(data=request.data)
        
        if serializer.is_valid():
            # Check if user is already a member
            user_id = serializer.validated_data.pop('user_id', None)  # Remove user_id from validated_data
            if not user_id:
                return Response(
                    {'error': 'user_id is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user = get_object_or_404(User, public_id=user_id)
            
            if ProjectMembership.objects.filter(project=project, user=user).exists():
                return Response(
                    {'error': 'User is already a project member'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Save with the actual user object, not user_id
            membership = serializer.save(project=project, user=user)
            
            # Re-serialize to get the full response with user details
            response_serializer = ProjectMembershipSerializer(membership)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated, IsProjectManagerOrOwner])
    def remove_member(self, request, public_id=None):
        """Remove a team member from the project"""
        project = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        membership = get_object_or_404(
            ProjectMembership,
            project=project,
            user__public_id=user_id
        )
        
        # Can't remove the owner
        if membership.role == 'owner':
            return Response(
                {'error': 'Cannot remove project owner'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        membership.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['get'])
    def tasks(self, request, public_id=None):
        """Get all tasks for a project"""
        project = self.get_object()
        tasks = project.tasks.filter(is_deleted=False)
        
        # Apply filters
        status_filter = request.query_params.get('status')
        if status_filter:
            tasks = tasks.filter(status=status_filter)
        
        assignee_filter = request.query_params.get('assignee')
        if assignee_filter:
            tasks = tasks.filter(assignee__public_id=assignee_filter)
        
        serializer = TaskListSerializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, public_id=None):
        """Get project statistics"""
        project = self.get_object()
        tasks = project.tasks.filter(is_deleted=False)
        
        stats = {
            'total_members': project.team_members.count(),
            'total_tasks': tasks.count(),
            'tasks_by_status': {
                'todo': tasks.filter(status='todo').count(),
                'in_progress': tasks.filter(status='in_progress').count(),
                'review': tasks.filter(status='review').count(),
                'done': tasks.filter(status='done').count(),
                'blocked': tasks.filter(status='blocked').count(),
            },
            'tasks_by_priority': {
                'low': tasks.filter(priority='low').count(),
                'medium': tasks.filter(priority='medium').count(),
                'high': tasks.filter(priority='high').count(),
                'critical': tasks.filter(priority='critical').count(),
            },
            'average_story_points': tasks.aggregate(Avg('story_points'))['story_points__avg'] or 0,
            'total_story_points': sum(t.story_points for t in tasks),
            'completed_story_points': sum(t.story_points for t in tasks.filter(status='done')),
        }
        
        return Response(stats)


class SprintViewSet(viewsets.ModelViewSet):
    """ViewSet for Sprint management"""
    permission_classes = [IsAuthenticated, IsProjectMember]
    lookup_field = 'public_id'
    
    def get_queryset(self):
        """Filter sprints by project if specified"""
        queryset = Sprint.objects.all()
        project_id = self.request.query_params.get('project')
        
        if project_id:
            queryset = queryset.filter(project__public_id=project_id)
        
        # Only show sprints for projects where user is a member
        user = self.request.user
        queryset = queryset.filter(
            Q(project__owner=user) | Q(project__team_members=user)
        ).distinct()
        
        return queryset.select_related('project').order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SprintSummarySerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return SprintCreateUpdateSerializer
        return SprintDetailSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'activate']:
            return [IsAuthenticated(), IsProjectManagerOrOwner()]
        return [IsAuthenticated(), IsProjectMember()]
    
    @action(detail=True, methods=['post'])
    def activate(self, request, public_id=None):
        """Activate a sprint (deactivates others in the project)"""
        sprint = self.get_object()
        
        # Check permission
        if sprint.project.owner != request.user:
            membership = sprint.project.projectmembership_set.filter(
                user=request.user,
                role__in=['owner', 'manager']
            ).first()
            if not membership:
                raise PermissionDenied("You don't have permission to manage sprints")
        
        # Deactivate other sprints in the project
        Sprint.objects.filter(
            project=sprint.project,
            is_active=True
        ).exclude(pk=sprint.pk).update(is_active=False)
        
        # Activate this sprint
        sprint.is_active = True
        sprint.updated_by = request.user
        sprint.save()
        
        serializer = SprintDetailSerializer(sprint)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, public_id=None):
        """Deactivate a sprint"""
        sprint = self.get_object()
        
        # Check permission
        if sprint.project.owner != request.user:
            membership = sprint.project.projectmembership_set.filter(
                user=request.user,
                role__in=['owner', 'manager']
            ).first()
            if not membership:
                raise PermissionDenied("You don't have permission to manage sprints")
        
        sprint.is_active = False
        sprint.updated_by = request.user
        sprint.save()
        
        serializer = SprintDetailSerializer(sprint)
        return Response(serializer.data)


class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet for Task management"""
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'priority', 'due_date', 'status']
    ordering = ['priority', '-created_at']
    lookup_field = 'public_id'
    
    def get_queryset(self):
        """Filter tasks for projects where user is a member"""
        user = self.request.user
        queryset = Task.objects.filter(
            Q(project__owner=user) | Q(project__team_members=user),
            is_deleted=False
        ).distinct()
        
        # Apply project filter if specified
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project__public_id=project_id)
        
        return queryset.select_related(
            'project', 'sprint', 'assignee', 'created_by', 'updated_by'
        ).prefetch_related('comments')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TaskListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return TaskCreateUpdateSerializer
        return TaskDetailSerializer
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), IsTaskAssigneeOrManager()]
        elif self.action in ['create', 'destroy']:
            return [IsAuthenticated(), IsProjectManagerOrOwner()]
        return [IsAuthenticated(), IsProjectMember()]
    
    def perform_create(self, serializer):
        """Set the project for the task"""
        project_id = self.request.data.get('project_id')
        if not project_id:
            raise ValidationError({'project_id': 'This field is required'})
        
        project = get_object_or_404(Project, public_id=project_id)
        
        # Check if user can create tasks in this project
        if not IsProjectMember().has_object_permission(self.request, self, project):
            raise PermissionDenied("You don't have permission to create tasks in this project")
        
        serializer.save(project=project)
    
    @action(detail=True, methods=['post'])
    def add_comment(self, request, public_id=None):
        """Add a comment to a task"""
        task = self.get_object()
        serializer = CommentSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            serializer.save(task=task)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, public_id=None):
        """Quick status update for a task"""
        task = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(Task.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        task.status = new_status
        task.updated_by = request.user
        task.save()
        
        serializer = TaskDetailSerializer(task)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet for Comment management"""
    permission_classes = [IsAuthenticated, IsCommentAuthorOrManager]
    serializer_class = CommentSerializer
    lookup_field = 'public_id'
    
    def get_queryset(self):
        """Filter comments for tasks in projects where user is a member"""
        user = self.request.user
        return Comment.objects.filter(
            Q(task__project__owner=user) | Q(task__project__team_members=user)
        ).distinct().select_related('author', 'task')