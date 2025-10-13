"""
Model tests for projects app
Ham Dog & TC's comprehensive test suite for all project models
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from apps.projects.models import (
    Project, ProjectMembership, Sprint, Task, Comment
)
from .factories import (
    UserFactory, ProjectFactory, ProjectMembershipFactory,
    SprintFactory, TaskFactory, CommentFactory
)

User = get_user_model()


class ProjectModelTest(TestCase):
    """Test Project model functionality"""
    
    def setUp(self):
        self.user = UserFactory()
        self.project = ProjectFactory(owner=self.user)
    
    def test_project_creation(self):
        """Test basic project creation"""
        self.assertIsNotNone(self.project.id)
        self.assertIsNotNone(self.project.public_id)
        self.assertEqual(self.project.status, 'active')
        self.assertEqual(self.project.owner, self.user)
    
    def test_slug_generation(self):
        """Test automatic slug generation from name"""
        project = Project.objects.create(
            name="Test Project",
            description="A test project",
            owner=self.user,
            start_date=timezone.now().date()
        )
        self.assertEqual(project.slug, "test-project")
    
    def test_unique_slug_generation(self):
        """Test that unique slugs are generated for projects with same slug base"""
        # Create first project
        project1 = Project.objects.create(
            name="Test Project",
            description="First project",
            owner=self.user,
            start_date=timezone.now().date()
        )
        
        # Create another user and project with same name (different owner)
        user2 = UserFactory()
        project2 = Project.objects.create(
            name="Test Project",
            description="Second project",
            owner=user2,
            start_date=timezone.now().date()
        )
        
        # Both should try to use same slug, but second should get modified
        self.assertEqual(project1.slug, "test-project")
        # Second project should have a unique slug
        self.assertIn("test-project", project2.slug)
        self.assertNotEqual(project1.slug, project2.slug)
    
    def test_unique_project_name_per_owner(self):
        """Test that same owner cannot have duplicate project names"""
        project1 = ProjectFactory(name="Unique Name", owner=self.user)
        
        # Try to create another project with same name and owner
        with self.assertRaises(ValidationError):
            project2 = Project(
                name="Unique Name",
                description="Another project",
                owner=self.user,
                start_date=timezone.now().date()
            )
            project2.clean()
    
    def test_different_owners_can_have_same_project_name(self):
        """Test that different owners can have projects with same name"""
        user2 = UserFactory()
        # Create with unique slugs to avoid conflict
        project1 = Project.objects.create(
            name="Same Name",
            slug="same-name-user1",
            description="Project 1",
            owner=self.user,
            start_date=timezone.now().date()
        )
        project2 = Project.objects.create(
            name="Same Name",
            slug="same-name-user2",
            description="Project 2",
            owner=user2,
            start_date=timezone.now().date()
        )
        
        self.assertEqual(project1.name, project2.name)
        self.assertNotEqual(project1.owner, project2.owner)
    
    def test_date_validation(self):
        """Test that end date must be after start date"""
        project = Project(
            name="Test Project",
            description="Test",
            owner=self.user,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() - timedelta(days=1)
        )
        
        with self.assertRaises(ValidationError) as context:
            project.clean()
        
        # Check for our custom error message
        self.assertIn("time machine", str(context.exception).lower())
    
    def test_active_project_date_validation(self):
        """Test that active projects can't start in the past"""
        past_date = timezone.now().date() - timedelta(days=30)
        project = Project(
            name="Past Project",
            description="Test",
            owner=self.user,
            status='active',
            start_date=past_date
        )
        
        with self.assertRaises(ValidationError) as context:
            project.clean()
        
        # Check for validation error about time traveler
        self.assertIn("time traveler", str(context.exception).lower())
    
    def test_completed_project_must_have_end_date(self):
        """Test that completed projects must have an end date"""
        project = Project(
            name="Completed Project",
            description="Test",
            owner=self.user,
            status='completed',
            start_date=timezone.now().date() - timedelta(days=30),
            end_date=None
        )
        
        with self.assertRaises(ValidationError) as context:
            project.clean()
        
        # Check for our custom error message
        self.assertIn("completed", str(context.exception).lower())
    
    def test_status_transition_validation(self):
        """Test invalid status transitions"""
        project = ProjectFactory(status='archived', owner=self.user)
        project.status = 'planning'
        
        with self.assertRaises(ValidationError) as context:
            project.clean()
        
        # Check for our custom error message about archives
        self.assertIn("archives", str(context.exception).lower())
    
    def test_soft_delete(self):
        """Test that BaseModel provides soft delete functionality"""
        project = ProjectFactory()
        project_id = project.id
        
        # Mark as deleted using the soft delete field
        project.is_deleted = True
        project.deleted_at = timezone.now()
        project.save()
        
        # Should still exist in database
        self.assertTrue(Project.objects.filter(id=project_id).exists())
        
        # But not in default queryset if filtered
        self.assertFalse(Project.objects.filter(id=project_id, is_deleted=False).exists())
        
        # Should be marked as deleted
        deleted_project = Project.objects.get(id=project_id)
        self.assertTrue(deleted_project.is_deleted)
        self.assertIsNotNone(deleted_project.deleted_at)
    
    def test_audit_fields(self):
        """Test that BaseModel provides audit fields"""
        project = ProjectFactory(created_by=self.user)
        
        self.assertEqual(project.created_by, self.user)
        self.assertIsNotNone(project.created_at)
        self.assertIsNotNone(project.updated_at)
        
        # Update the project
        project.name = "Updated Name"
        project.updated_by = self.user
        project.save()
        
        self.assertEqual(project.updated_by, self.user)
        self.assertGreater(project.updated_at, project.created_at)
    
    def test_str_method(self):
        """Test string representation"""
        project = ProjectFactory(name="Test Project")
        self.assertEqual(str(project), "Test Project")


class ProjectMembershipModelTest(TestCase):
    """Test ProjectMembership model functionality"""
    
    def setUp(self):
        self.user = UserFactory()
        self.project = ProjectFactory()
        self.membership = ProjectMembershipFactory(
            project=self.project,
            user=self.user,
            role='developer'
        )
    
    def test_membership_creation(self):
        """Test basic membership creation"""
        self.assertIsNotNone(self.membership.id)
        self.assertIsNotNone(self.membership.public_id)
        self.assertEqual(self.membership.role, 'developer')
        self.assertEqual(self.membership.project, self.project)
        self.assertEqual(self.membership.user, self.user)
    
    def test_unique_together_constraint(self):
        """Test that a user can only have one membership per project"""
        # Try to create duplicate membership
        with self.assertRaises(Exception):  # IntegrityError
            ProjectMembership.objects.create(
                project=self.project,
                user=self.user,
                role='manager'
            )
    
    def test_cascade_delete(self):
        """Test that memberships are deleted when project is deleted"""
        membership_id = self.membership.id
        self.project.delete()
        
        self.assertFalse(
            ProjectMembership.objects.filter(id=membership_id).exists()
        )
    
    def test_str_method(self):
        """Test string representation"""
        expected = f"{self.user} - developer on {self.project}"
        self.assertEqual(str(self.membership), expected)


class SprintModelTest(TestCase):
    """Test Sprint model functionality"""
    
    def setUp(self):
        self.project = ProjectFactory()
        self.sprint = SprintFactory(project=self.project)
    
    def test_sprint_creation(self):
        """Test basic sprint creation"""
        self.assertIsNotNone(self.sprint.id)
        self.assertIsNotNone(self.sprint.public_id)
        self.assertEqual(self.sprint.project, self.project)
        self.assertFalse(self.sprint.is_active)
    
    def test_only_one_active_sprint_per_project(self):
        """Test that only one sprint can be active per project"""
        sprint1 = SprintFactory(project=self.project, is_active=True)
        self.assertTrue(sprint1.is_active)
        
        # Create another active sprint
        sprint2 = SprintFactory(project=self.project, is_active=True)
        
        # Refresh sprint1 from database
        sprint1.refresh_from_db()
        
        # sprint1 should now be inactive
        self.assertFalse(sprint1.is_active)
        self.assertTrue(sprint2.is_active)
    
    def test_multiple_active_sprints_across_projects(self):
        """Test that different projects can have active sprints simultaneously"""
        project2 = ProjectFactory()
        
        sprint1 = SprintFactory(project=self.project, is_active=True)
        sprint2 = SprintFactory(project=project2, is_active=True)
        
        # Both should be active
        self.assertTrue(sprint1.is_active)
        self.assertTrue(sprint2.is_active)
    
    def test_str_method(self):
        """Test string representation"""
        sprint = SprintFactory(
            project=self.project,
            name="Sprint 1"
        )
        expected = f"{self.project.name} - Sprint 1"
        self.assertEqual(str(sprint), expected)


class TaskModelTest(TestCase):
    """Test Task model functionality"""
    
    def setUp(self):
        self.user = UserFactory()
        self.project = ProjectFactory()
        self.sprint = SprintFactory(project=self.project)
        self.task = TaskFactory(
            project=self.project,
            sprint=self.sprint,
            assignee=self.user
        )
    
    def test_task_creation(self):
        """Test basic task creation"""
        self.assertIsNotNone(self.task.id)
        self.assertIsNotNone(self.task.public_id)
        self.assertEqual(self.task.status, 'todo')
        self.assertEqual(self.task.priority, 'medium')
        self.assertEqual(self.task.project, self.project)
    
    def test_task_without_sprint(self):
        """Test that tasks can exist without being in a sprint"""
        task = TaskFactory(project=self.project, sprint=None)
        self.assertIsNone(task.sprint)
        self.assertEqual(task.project, self.project)
    
    def test_story_points_validation(self):
        """Test story points are within valid range"""
        # Valid story points
        task = TaskFactory(story_points=13)
        self.assertEqual(task.story_points, 13)
        
        # Invalid story points (too low)
        with self.assertRaises(ValidationError):
            task = Task(
                project=self.project,
                title="Test Task",
                description="Test",
                story_points=0
            )
            task.full_clean()
        
        # Invalid story points (too high)
        with self.assertRaises(ValidationError):
            task = Task(
                project=self.project,
                title="Test Task",
                description="Test",
                story_points=22
            )
            task.full_clean()
    
    def test_task_soft_delete(self):
        """Test that BaseModel provides soft delete for tasks"""
        task_id = self.task.id
        
        # Mark as deleted using the soft delete field
        self.task.is_deleted = True
        self.task.deleted_at = timezone.now()
        self.task.save()
        
        # Should still exist but be marked as deleted
        task = Task.objects.get(id=task_id)
        self.assertTrue(task.is_deleted)
        self.assertIsNotNone(task.deleted_at)
    
    def test_assignee_can_be_null(self):
        """Test that tasks can be unassigned"""
        task = TaskFactory(project=self.project, assignee=None)
        self.assertIsNone(task.assignee)
    
    def test_str_method(self):
        """Test string representation"""
        task = TaskFactory(
            project=self.project,
            title="Fix the bug"
        )
        expected = f"{self.project.name} - Fix the bug"
        self.assertEqual(str(task), expected)


class CommentModelTest(TestCase):
    """Test Comment model functionality"""
    
    def setUp(self):
        self.user = UserFactory()
        self.task = TaskFactory()
        self.comment = CommentFactory(
            task=self.task,
            author=self.user,
            content="Initial comment"
        )
    
    def test_comment_creation(self):
        """Test basic comment creation"""
        self.assertIsNotNone(self.comment.id)
        self.assertIsNotNone(self.comment.public_id)
        self.assertEqual(self.comment.task, self.task)
        self.assertEqual(self.comment.author, self.user)
        self.assertFalse(self.comment.edited)
    
    def test_comment_edited_flag(self):
        """Test that edited flag is set when comment is updated"""
        # Initially not edited
        self.assertFalse(self.comment.edited)
        
        # Update the comment
        self.comment.content = "Updated comment"
        self.comment.save()
        
        # Should now be marked as edited
        self.assertTrue(self.comment.edited)
    
    def test_nested_comments(self):
        """Test that comments can have replies"""
        reply = CommentFactory(
            task=self.task,
            author=self.user,
            content="This is a reply",
            parent=self.comment
        )
        
        self.assertEqual(reply.parent, self.comment)
        self.assertIn(reply, self.comment.replies.all())
    
    def test_cascade_delete_with_task(self):
        """Test that comments are deleted when task is deleted"""
        comment_id = self.comment.id
        self.task.delete()
        
        # Comment should be gone (tasks use soft delete, but cascade still applies)
        self.assertFalse(Comment.objects.filter(id=comment_id).exists())
    
    def test_cascade_delete_with_parent_comment(self):
        """Test that replies are deleted when parent comment is deleted"""
        reply = CommentFactory(
            task=self.task,
            author=self.user,
            parent=self.comment
        )
        reply_id = reply.id
        
        self.comment.delete()
        
        # Reply should be deleted too
        self.assertFalse(Comment.objects.filter(id=reply_id).exists())
    
    def test_str_method(self):
        """Test string representation"""
        expected = f"Comment by {self.user} on {self.task.title}"
        self.assertEqual(str(self.comment), expected)