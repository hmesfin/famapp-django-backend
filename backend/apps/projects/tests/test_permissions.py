"""
Permission tests for projects app
Ham Dog & TC's comprehensive permission testing suite
"""
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from django.contrib.auth import get_user_model

from apps.projects.permissions import (
    IsProjectOwner, IsProjectMember, IsProjectManagerOrOwner,
    IsTaskAssigneeOrManager, IsCommentAuthorOrManager, CanManageProjectTeam
)
from apps.projects.models import ProjectMembership
from .factories import (
    UserFactory, ProjectFactory, ProjectMembershipFactory,
    TaskFactory, CommentFactory, SprintFactory
)

User = get_user_model()


class PermissionTestBase(TestCase):
    """Base class for permission tests"""
    
    def setUp(self):
        self.factory = APIRequestFactory()
        self.owner = UserFactory()
        self.manager = UserFactory()
        self.developer = UserFactory()
        self.viewer = UserFactory()
        self.outsider = UserFactory()
        
        # Create project with owner
        self.project = ProjectFactory(owner=self.owner)
        
        # Add team members
        self.manager_membership = ProjectMembershipFactory(
            project=self.project,
            user=self.manager,
            role='manager'
        )
        self.developer_membership = ProjectMembershipFactory(
            project=self.project,
            user=self.developer,
            role='developer'
        )
        self.viewer_membership = ProjectMembershipFactory(
            project=self.project,
            user=self.viewer,
            role='viewer'
        )
        
        # Create test objects
        self.task = TaskFactory(project=self.project, assignee=self.developer)
        self.sprint = SprintFactory(project=self.project)
        self.comment = CommentFactory(task=self.task, author=self.developer)
    
    def create_request(self, user, method='GET'):
        """Helper to create a request with a user"""
        request = getattr(self.factory, method.lower())('/')
        request.user = user
        return request


class IsProjectOwnerTest(PermissionTestBase):
    """Test IsProjectOwner permission"""
    
    def setUp(self):
        super().setUp()
        self.permission = IsProjectOwner()
    
    def test_owner_has_permission_on_project(self):
        """Test that owner has permission on their project"""
        request = self.create_request(self.owner)
        self.assertTrue(
            self.permission.has_object_permission(request, None, self.project)
        )
    
    def test_non_owner_denied_permission_on_project(self):
        """Test that non-owners are denied permission"""
        for user in [self.manager, self.developer, self.viewer, self.outsider]:
            request = self.create_request(user)
            self.assertFalse(
                self.permission.has_object_permission(request, None, self.project)
            )
    
    def test_owner_has_permission_on_task(self):
        """Test that owner has permission on tasks in their project"""
        request = self.create_request(self.owner)
        self.assertTrue(
            self.permission.has_object_permission(request, None, self.task)
        )
    
    def test_owner_has_permission_on_sprint(self):
        """Test that owner has permission on sprints in their project"""
        request = self.create_request(self.owner)
        self.assertTrue(
            self.permission.has_object_permission(request, None, self.sprint)
        )


class IsProjectMemberTest(PermissionTestBase):
    """Test IsProjectMember permission"""
    
    def setUp(self):
        super().setUp()
        self.permission = IsProjectMember()
    
    def test_owner_is_member(self):
        """Test that owner is considered a member"""
        request = self.create_request(self.owner)
        self.assertTrue(
            self.permission.has_object_permission(request, None, self.project)
        )
    
    def test_team_members_have_access(self):
        """Test that all team members have access"""
        for user in [self.manager, self.developer, self.viewer]:
            request = self.create_request(user)
            self.assertTrue(
                self.permission.has_object_permission(request, None, self.project)
            )
    
    def test_outsider_denied_access(self):
        """Test that non-members are denied access"""
        request = self.create_request(self.outsider)
        self.assertFalse(
            self.permission.has_object_permission(request, None, self.project)
        )
    
    def test_member_access_to_task(self):
        """Test member access to project tasks"""
        request = self.create_request(self.developer)
        self.assertTrue(
            self.permission.has_object_permission(request, None, self.task)
        )
    
    def test_outsider_denied_task_access(self):
        """Test outsider denied access to tasks"""
        request = self.create_request(self.outsider)
        self.assertFalse(
            self.permission.has_object_permission(request, None, self.task)
        )


class IsProjectManagerOrOwnerTest(PermissionTestBase):
    """Test IsProjectManagerOrOwner permission"""
    
    def setUp(self):
        super().setUp()
        self.permission = IsProjectManagerOrOwner()
    
    def test_read_access_for_all_members(self):
        """Test that all members have read access"""
        for user in [self.owner, self.manager, self.developer, self.viewer]:
            request = self.create_request(user, 'GET')
            self.assertTrue(
                self.permission.has_object_permission(request, None, self.project)
            )
    
    def test_write_access_for_owner(self):
        """Test that owner has write access"""
        request = self.create_request(self.owner, 'PUT')
        self.assertTrue(
            self.permission.has_object_permission(request, None, self.project)
        )
    
    def test_write_access_for_manager(self):
        """Test that manager has write access"""
        request = self.create_request(self.manager, 'PUT')
        self.assertTrue(
            self.permission.has_object_permission(request, None, self.project)
        )
    
    def test_no_write_access_for_developer(self):
        """Test that developer has no write access"""
        request = self.create_request(self.developer, 'PUT')
        self.assertFalse(
            self.permission.has_object_permission(request, None, self.project)
        )
    
    def test_no_write_access_for_viewer(self):
        """Test that viewer has no write access"""
        request = self.create_request(self.viewer, 'PUT')
        self.assertFalse(
            self.permission.has_object_permission(request, None, self.project)
        )
    
    def test_outsider_denied_all_access(self):
        """Test that outsider has no access at all"""
        for method in ['GET', 'PUT', 'DELETE']:
            request = self.create_request(self.outsider, method)
            self.assertFalse(
                self.permission.has_object_permission(request, None, self.project)
            )
    
    def test_manager_can_modify_task(self):
        """Test that manager can modify tasks"""
        request = self.create_request(self.manager, 'PUT')
        self.assertTrue(
            self.permission.has_object_permission(request, None, self.task)
        )


class IsTaskAssigneeOrManagerTest(PermissionTestBase):
    """Test IsTaskAssigneeOrManager permission"""
    
    def setUp(self):
        super().setUp()
        self.permission = IsTaskAssigneeOrManager()
    
    def test_assignee_can_update_task(self):
        """Test that assignee can update their task"""
        request = self.create_request(self.developer, 'PUT')
        self.assertTrue(
            self.permission.has_object_permission(request, None, self.task)
        )
    
    def test_owner_can_update_any_task(self):
        """Test that owner can update any task"""
        request = self.create_request(self.owner, 'PUT')
        self.assertTrue(
            self.permission.has_object_permission(request, None, self.task)
        )
    
    def test_manager_can_update_any_task(self):
        """Test that manager can update any task"""
        request = self.create_request(self.manager, 'PUT')
        self.assertTrue(
            self.permission.has_object_permission(request, None, self.task)
        )
    
    def test_non_assignee_developer_cannot_update(self):
        """Test that non-assignee developer cannot update task"""
        other_developer = UserFactory()
        ProjectMembershipFactory(
            project=self.project,
            user=other_developer,
            role='developer'
        )
        request = self.create_request(other_developer, 'PUT')
        self.assertFalse(
            self.permission.has_object_permission(request, None, self.task)
        )
    
    def test_viewer_cannot_update_task(self):
        """Test that viewer cannot update tasks"""
        request = self.create_request(self.viewer, 'PUT')
        self.assertFalse(
            self.permission.has_object_permission(request, None, self.task)
        )
    
    def test_all_members_can_read_task(self):
        """Test that all project members can read tasks"""
        for user in [self.owner, self.manager, self.developer, self.viewer]:
            request = self.create_request(user, 'GET')
            self.assertTrue(
                self.permission.has_object_permission(request, None, self.task)
            )


class IsCommentAuthorOrManagerTest(PermissionTestBase):
    """Test IsCommentAuthorOrManager permission"""
    
    def setUp(self):
        super().setUp()
        self.permission = IsCommentAuthorOrManager()
    
    def test_author_can_edit_comment(self):
        """Test that comment author can edit their comment"""
        request = self.create_request(self.developer, 'PUT')
        self.assertTrue(
            self.permission.has_object_permission(request, None, self.comment)
        )
    
    def test_author_can_delete_comment(self):
        """Test that comment author can delete their comment"""
        request = self.create_request(self.developer, 'DELETE')
        self.assertTrue(
            self.permission.has_object_permission(request, None, self.comment)
        )
    
    def test_manager_can_moderate_comment(self):
        """Test that manager can moderate comments"""
        request = self.create_request(self.manager, 'DELETE')
        self.assertTrue(
            self.permission.has_object_permission(request, None, self.comment)
        )
    
    def test_owner_can_moderate_comment(self):
        """Test that owner can moderate comments"""
        request = self.create_request(self.owner, 'DELETE')
        self.assertTrue(
            self.permission.has_object_permission(request, None, self.comment)
        )
    
    def test_other_member_cannot_edit_comment(self):
        """Test that other members cannot edit comments"""
        other_developer = UserFactory()
        ProjectMembershipFactory(
            project=self.project,
            user=other_developer,
            role='developer'
        )
        request = self.create_request(other_developer, 'PUT')
        self.assertFalse(
            self.permission.has_object_permission(request, None, self.comment)
        )
    
    def test_all_members_can_read_comments(self):
        """Test that all project members can read comments"""
        for user in [self.owner, self.manager, self.developer, self.viewer]:
            request = self.create_request(user, 'GET')
            self.assertTrue(
                self.permission.has_object_permission(request, None, self.comment)
            )
    
    def test_outsider_cannot_read_comments(self):
        """Test that outsiders cannot read comments"""
        request = self.create_request(self.outsider, 'GET')
        self.assertFalse(
            self.permission.has_object_permission(request, None, self.comment)
        )


class CanManageProjectTeamTest(PermissionTestBase):
    """Test CanManageProjectTeam permission"""
    
    def setUp(self):
        super().setUp()
        self.permission = CanManageProjectTeam()
    
    def test_authenticated_user_has_base_permission(self):
        """Test that authenticated users have base permission"""
        request = self.create_request(self.owner)
        self.assertTrue(
            self.permission.has_permission(request, None)
        )
    
    def test_owner_can_manage_team(self):
        """Test that owner can manage team members"""
        request = self.create_request(self.owner)
        self.assertTrue(
            self.permission.has_object_permission(
                request, None, self.developer_membership
            )
        )
    
    def test_manager_can_manage_team(self):
        """Test that manager can manage team members"""
        request = self.create_request(self.manager)
        self.assertTrue(
            self.permission.has_object_permission(
                request, None, self.developer_membership
            )
        )
    
    def test_developer_cannot_manage_team(self):
        """Test that developer cannot manage team"""
        request = self.create_request(self.developer)
        self.assertFalse(
            self.permission.has_object_permission(
                request, None, self.viewer_membership
            )
        )
    
    def test_viewer_cannot_manage_team(self):
        """Test that viewer cannot manage team"""
        request = self.create_request(self.viewer)
        self.assertFalse(
            self.permission.has_object_permission(
                request, None, self.developer_membership
            )
        )
    
    def test_outsider_cannot_manage_team(self):
        """Test that outsider cannot manage team"""
        request = self.create_request(self.outsider)
        self.assertFalse(
            self.permission.has_object_permission(
                request, None, self.developer_membership
            )
        )