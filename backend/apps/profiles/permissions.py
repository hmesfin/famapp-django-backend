"""
Custom permissions for profiles app
Ham Dog & TC's permission guards!
"""
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of a profile to edit it.
    Read permissions are allowed to any request.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the profile
        return obj.user == request.user


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners to access their own objects.
    """
    
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user