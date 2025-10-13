"""
Invitation statistics service
Extracted from InvitationViewSet stats action

Ham Dog's Analytics Philosophy:
- Provide meaningful metrics
- Calculate acceptance rates and timing
- Support different permission levels
"""

from typing import Dict, Any
from django.contrib.auth import get_user_model
from django.db.models import Count, Q, Avg, F, Case, When, FloatField
from django.db.models.functions import Extract
from django.utils import timezone
from datetime import timedelta

from apps.invitations.models import Invitation
from apps.invitations.utils.query_debugging import monitor_invitation_queries, log_slow_queries

User = get_user_model()


class InvitationStatsService:
    """
    Handles invitation statistics and analytics
    
    Provides:
    - Overall invitation statistics
    - Acceptance rate calculations
    - Average acceptance time analysis
    - Permission-based data access
    """
    
    def __init__(self, permission_service=None):
        """Initialize stats service with optional permission service injection"""
        if permission_service is None:
            from apps.invitations.services.permission_service import PermissionService
            permission_service = PermissionService()
        self.permission_service = permission_service
    
    @monitor_invitation_queries
    def calculate_stats(self, user: User) -> Dict[str, Any]:
        """
        Calculate comprehensive invitation statistics
        
        Args:
            user: User requesting statistics
            
        Returns:
            dict: Detailed statistics
        """
        queryset = Invitation.objects.active()
        
        # Basic counts
        stats = self._calculate_basic_counts(queryset)
        
        # Calculate acceptance rate
        stats['acceptance_rate'] = self._calculate_acceptance_rate(queryset)
        
        # Calculate average acceptance time
        stats['average_acceptance_time'] = self._calculate_avg_acceptance_time(queryset)
        
        return stats
    
    def get_pending_count(self, user: User) -> int:
        """
        Get count of pending invitations based on user permissions
        Optimized with proper filtering
        
        Args:
            user: User requesting the count
            
        Returns:
            int: Count of pending invitations
        """
        queryset = Invitation.objects.active().filter(status='pending')
        
        # Admins see all pending, others see only their own
        if not self.permission_service.can_view_all_invitations(user):
            queryset = queryset.filter(invited_by=user)
        
        # Use exists() for boolean checks or count() for actual counts
        return queryset.count()
    
    @log_slow_queries
    def get_user_invitation_stats(self, user: User) -> Dict[str, Any]:
        """
        Get invitation statistics for a specific user using single aggregated query
        
        Args:
            user: User to get statistics for
            
        Returns:
            dict: User-specific invitation statistics
        """
        queryset = Invitation.objects.active().filter(invited_by=user)
        
        # Single aggregated query instead of multiple count() calls
        stats = queryset.aggregate(
            total_sent=Count('id'),
            pending=Count('id', filter=Q(status='pending')),
            accepted=Count('id', filter=Q(status='accepted')),
            expired=Count('id', filter=Q(status='expired')),
            cancelled=Count('id', filter=Q(status='cancelled'))
        )
        
        return {
            'total_sent': stats['total_sent'] or 0,
            'pending': stats['pending'] or 0,
            'accepted': stats['accepted'] or 0,
            'expired': stats['expired'] or 0,
            'cancelled': stats['cancelled'] or 0,
        }
    
    def get_role_distribution(self, user: User) -> Dict[str, int]:
        """
        Get distribution of invitations by role with permission filtering
        
        Args:
            user: User requesting the distribution
            
        Returns:
            dict: Role distribution statistics
        """
        queryset = Invitation.objects.active()
        
        # Apply permission-based filtering
        if not self.permission_service.can_view_all_invitations(user):
            queryset = queryset.filter(invited_by=user)
        
        # Aggregate by role
        role_stats = queryset.values('role').annotate(
            count=Count('role')
        ).order_by('role')
        
        return {stat['role']: stat['count'] for stat in role_stats}
    
    def _has_stats_permission(self, user: User) -> bool:
        """
        Check if user has permission to view statistics
        
        Args:
            user: User to check permissions for
            
        Returns:
            bool: True if user has stats permission
        """
        return self.permission_service.can_view_stats(user)
    
    def _calculate_basic_counts(self, queryset) -> Dict[str, int]:
        """
        Calculate basic invitation counts using single aggregated query
        
        Args:
            queryset: Invitation queryset to analyze
            
        Returns:
            dict: Basic count statistics
        """
        # Single query with conditional aggregation to avoid multiple counts
        stats = queryset.aggregate(
            total=Count('id'),
            pending=Count('id', filter=Q(status='pending')),
            accepted=Count('id', filter=Q(status='accepted')),
            expired=Count('id', filter=Q(status='expired')),
            cancelled=Count('id', filter=Q(status='cancelled'))
        )
        
        return {
            'total': stats['total'] or 0,
            'pending': stats['pending'] or 0,
            'accepted': stats['accepted'] or 0,
            'expired': stats['expired'] or 0,
            'cancelled': stats['cancelled'] or 0
        }
    
    def _calculate_acceptance_rate(self, queryset) -> float:
        """
        Calculate invitation acceptance rate using single aggregated query
        
        Args:
            queryset: Invitation queryset to analyze
            
        Returns:
            float: Acceptance rate as percentage
        """
        # Single aggregated query for acceptance rate calculation
        stats = queryset.aggregate(
            total=Count('id'),
            accepted=Count('id', filter=Q(status='accepted')),
            cancelled=Count('id', filter=Q(status='cancelled')),
            expired=Count('id', filter=Q(status='expired'))
        )
        
        total = stats['total'] or 0
        accepted = stats['accepted'] or 0
        cancelled = stats['cancelled'] or 0
        expired = stats['expired'] or 0
        
        # Calculate acceptance rate based on completed invitations
        completed = accepted + cancelled + expired
        
        if total > 0 and completed > 0:
            acceptance_rate = (accepted / completed) * 100
            return round(acceptance_rate, 2)
        
        return 0
    
    def _calculate_avg_acceptance_time(self, queryset) -> float:
        """
        Calculate average acceptance time in hours using database aggregation
        
        Args:
            queryset: Invitation queryset to analyze
            
        Returns:
            float: Average acceptance time in hours
        """
        # Use database-level calculation to avoid fetching all records
        avg_seconds = queryset.filter(
            status='accepted',
            accepted_at__isnull=False,
            created_at__isnull=False
        ).aggregate(
            avg_time=Avg(
                Extract(
                    F('accepted_at') - F('created_at'),
                    'epoch'
                )
            )
        )['avg_time']
        
        if avg_seconds:
            # Convert seconds to hours
            avg_hours = avg_seconds / 3600
            return round(avg_hours, 2)
        
        return 0