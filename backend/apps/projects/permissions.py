"""
Custom permissions for Project Management
RBAC implementation following Ham Dog & TC's security protocols
"""
from rest_framework import permissions
from apps.projects.models import ProjectMembership


class IsProjectOwner(permissions.BasePermission):
    """Only project owners can perform certain actions"""
    
    def has_object_permission(self, request, view, obj):
        # Handle different model types
        if hasattr(obj, 'project'):
            # For Task, Sprint, etc.
            project = obj.project
        else:
            # For Project model itself
            project = obj
        
        return project.owner == request.user


class IsProjectMember(permissions.BasePermission):
    """Check if user is a member of the project"""
    
    def has_object_permission(self, request, view, obj):
        # Handle different model types
        if hasattr(obj, 'project'):
            project = obj.project
        else:
            project = obj
        
        # Owner always has access
        if project.owner == request.user:
            return True
        
        # Check membership
        return ProjectMembership.objects.filter(
            project=project,
            user=request.user
        ).exists()


class IsProjectManagerOrOwner(permissions.BasePermission):
    """Only project managers or owners can modify project resources"""
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for all members
        if request.method in permissions.SAFE_METHODS:
            return IsProjectMember().has_object_permission(request, view, obj)
        
        # Handle different model types
        if hasattr(obj, 'project'):
            project = obj.project
        else:
            project = obj
        
        # Owner always has write access
        if project.owner == request.user:
            return True
        
        # Check if user is a manager
        membership = ProjectMembership.objects.filter(
            project=project,
            user=request.user
        ).first()
        
        return membership and membership.role in ['manager', 'owner']


class IsTaskAssigneeOrManager(permissions.BasePermission):
    """Task assignee can update their own tasks, managers can update any task"""
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for all project members
        if request.method in permissions.SAFE_METHODS:
            return IsProjectMember().has_object_permission(request, view, obj)
        
        # Assignee can update their own task
        if obj.assignee == request.user:
            return True
        
        # Managers and owners can update any task
        return IsProjectManagerOrOwner().has_object_permission(request, view, obj)


class IsCommentAuthorOrManager(permissions.BasePermission):
    """Comment authors can edit/delete their own comments"""
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for all project members
        if request.method in permissions.SAFE_METHODS:
            # Check if user is a member of the task's project
            return IsProjectMember().has_object_permission(request, view, obj.task)
        
        # Authors can edit/delete their own comments
        if obj.author == request.user:
            return True
        
        # Managers can moderate comments
        return IsProjectManagerOrOwner().has_object_permission(request, view, obj.task)


class CanManageProjectTeam(permissions.BasePermission):
    """Only owners and managers can manage team members"""
    
    def has_permission(self, request, view):
        # This will be checked at the view level with the project
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # obj here is a ProjectMembership
        project = obj.project
        
        # Owner can always manage team
        if project.owner == request.user:
            return True
        
        # Check if user is a manager
        membership = ProjectMembership.objects.filter(
            project=project,
            user=request.user
        ).first()
        
        return membership and membership.role == 'manager'