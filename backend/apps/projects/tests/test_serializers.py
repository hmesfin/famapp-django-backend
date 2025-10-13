"""
Serializer tests for projects app
Ham Dog & TC's comprehensive serializer validation tests
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request

from apps.projects.models import Project, ProjectMembership, Sprint, Task
from apps.projects.api.serializers import (
    ProjectCreateUpdateSerializer,
    ProjectListSerializer,
    ProjectDetailSerializer,
    ProjectMembershipSerializer,
    SprintCreateUpdateSerializer,
    SprintDetailSerializer,
    TaskCreateUpdateSerializer,
    TaskDetailSerializer,
    CommentSerializer,
    UserSummarySerializer
)
from .factories import (
    UserFactory, ProjectFactory, ProjectMembershipFactory,
    SprintFactory, TaskFactory, CommentFactory
)

User = get_user_model()


class SerializerTestBase(TestCase):
    """Base class for serializer tests"""
    
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = UserFactory()
        self.project = ProjectFactory(owner=self.user)
        
    def get_request(self, user=None):
        """Create a mock request with user"""
        request = self.factory.get('/')
        request.user = user or self.user
        return Request(request)


class ProjectSerializerTest(SerializerTestBase):
    """Test Project serializers"""
    
    def test_project_list_serializer(self):
        """Test ProjectListSerializer outputs correct fields"""
        # Add some team members and tasks
        ProjectMembershipFactory(project=self.project, user=UserFactory())
        ProjectMembershipFactory(project=self.project, user=UserFactory())
        TaskFactory(project=self.project)
        TaskFactory(project=self.project)
        
        serializer = ProjectListSerializer(self.project)
        data = serializer.data
        
        self.assertIn('public_id', data)
        self.assertIn('name', data)
        self.assertIn('slug', data)
        self.assertIn('status', data)
        self.assertIn('owner', data)
        self.assertIn('member_count', data)
        self.assertIn('task_count', data)
        self.assertEqual(data['member_count'], 3)  # owner + 2 members
        self.assertEqual(data['task_count'], 2)
    
    def test_project_detail_serializer(self):
        """Test ProjectDetailSerializer includes all details"""
        sprint = SprintFactory(project=self.project, is_active=True)
        TaskFactory(project=self.project, status='done')
        TaskFactory(project=self.project, status='in_progress')
        
        serializer = ProjectDetailSerializer(self.project)
        data = serializer.data
        
        self.assertIn('memberships', data)
        self.assertIn('active_sprint', data)
        self.assertIn('stats', data)
        self.assertIsNotNone(data['active_sprint'])
        self.assertEqual(data['stats']['total_tasks'], 2)
        self.assertEqual(data['stats']['completed_tasks'], 1)
    
    def test_project_create_serializer_valid_data(self):
        """Test creating project with valid data"""
        data = {
            'name': 'New Project',
            'description': 'A new project',
            'status': 'planning',
            'start_date': timezone.now().date(),
            'end_date': timezone.now().date() + timedelta(days=30)
        }
        
        serializer = ProjectCreateUpdateSerializer(
            data=data,
            context={'request': self.get_request()}
        )
        
        self.assertTrue(serializer.is_valid())
        project = serializer.save()
        
        self.assertEqual(project.name, 'New Project')
        self.assertEqual(project.owner, self.user)
        self.assertEqual(project.created_by, self.user)
        
        # Check owner was added as member
        membership = ProjectMembership.objects.filter(
            project=project,
            user=self.user
        ).first()
        self.assertIsNotNone(membership)
        self.assertEqual(membership.role, 'owner')
    
    def test_project_name_uniqueness_per_owner(self):
        """Test project name must be unique per owner"""
        existing_project = ProjectFactory(name="Unique Name", owner=self.user)
        
        data = {
            'name': 'Unique Name',
            'description': 'Another project',
            'start_date': timezone.now().date()
        }
        
        serializer = ProjectCreateUpdateSerializer(
            data=data,
            context={'request': self.get_request()}
        )
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)
        self.assertIn('already have a project named', str(serializer.errors['name']))
    
    def test_project_date_validation(self):
        """Test project date range validation"""
        data = {
            'name': 'Test Project',
            'description': 'Test',
            'start_date': timezone.now().date(),
            'end_date': timezone.now().date() - timedelta(days=1)  # Invalid
        }
        
        serializer = ProjectCreateUpdateSerializer(
            data=data,
            context={'request': self.get_request()}
        )
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('End date must be after start date', str(serializer.errors))
    
    def test_active_project_date_validation(self):
        """Test active projects must have started"""
        data = {
            'name': 'Future Project',
            'description': 'Test',
            'status': 'active',
            'start_date': timezone.now().date() + timedelta(days=30)
        }
        
        serializer = ProjectCreateUpdateSerializer(
            data=data,
            context={'request': self.get_request()}
        )
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('Active projects must have already started', str(serializer.errors))
    
    def test_completed_project_requires_end_date(self):
        """Test completed projects must have end date"""
        data = {
            'name': 'Completed Project',
            'description': 'Test',
            'status': 'completed',
            'start_date': timezone.now().date() - timedelta(days=30)
        }
        
        serializer = ProjectCreateUpdateSerializer(
            data=data,
            context={'request': self.get_request()}
        )
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('Completed projects must have an end date', str(serializer.errors))
    
    def test_status_transition_validation(self):
        """Test invalid status transitions are prevented"""
        project = ProjectFactory(status='archived', owner=self.user)
        
        serializer = ProjectCreateUpdateSerializer(
            instance=project,
            data={'status': 'planning'},
            partial=True,
            context={'request': self.get_request()}
        )
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('Invalid status transition', str(serializer.errors))


class SprintSerializerTest(SerializerTestBase):
    """Test Sprint serializers"""
    
    def test_sprint_detail_serializer(self):
        """Test SprintDetailSerializer includes stats"""
        sprint = SprintFactory(project=self.project)
        TaskFactory(project=self.project, sprint=sprint, story_points=5, status='done')
        TaskFactory(project=self.project, sprint=sprint, story_points=3, status='todo')
        
        serializer = SprintDetailSerializer(sprint)
        data = serializer.data
        
        self.assertIn('stats', data)
        self.assertEqual(data['stats']['total_tasks'], 2)
        self.assertEqual(data['stats']['total_story_points'], 8)
        self.assertEqual(data['stats']['completed_story_points'], 5)
        self.assertEqual(data['stats']['completion_percentage'], 62.5)
    
    def test_sprint_create_valid_data(self):
        """Test creating sprint with valid data"""
        data = {
            'project_id': str(self.project.public_id),
            'name': 'Sprint 1',
            'goal': 'Complete MVP',
            'start_date': timezone.now().date(),
            'end_date': timezone.now().date() + timedelta(days=14),
            'is_active': True
        }
        
        serializer = SprintCreateUpdateSerializer(
            data=data,
            context={'request': self.get_request()}
        )
        
        self.assertTrue(serializer.is_valid())
        sprint = serializer.save()
        
        self.assertEqual(sprint.project, self.project)
        self.assertEqual(sprint.name, 'Sprint 1')
        self.assertTrue(sprint.is_active)
    
    def test_sprint_date_validation(self):
        """Test sprint date range validation"""
        data = {
            'project_id': str(self.project.public_id),
            'name': 'Sprint 1',
            'goal': 'Complete MVP',
            'start_date': timezone.now().date(),
            'end_date': timezone.now().date() - timedelta(days=1)  # Invalid
        }
        
        serializer = SprintCreateUpdateSerializer(
            data=data,
            context={'request': self.get_request()}
        )
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('end_date', serializer.errors)
        self.assertIn('End date must be after start date', str(serializer.errors['end_date']))
    
    def test_only_one_active_sprint_per_project(self):
        """Test project can only have one active sprint"""
        # Create an active sprint
        SprintFactory(project=self.project, is_active=True)
        
        data = {
            'project_id': str(self.project.public_id),
            'name': 'Sprint 2',
            'goal': 'Another sprint',
            'start_date': timezone.now().date(),
            'end_date': timezone.now().date() + timedelta(days=14),
            'is_active': True
        }
        
        serializer = SprintCreateUpdateSerializer(
            data=data,
            context={'request': self.get_request()}
        )
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('is_active', serializer.errors)
        self.assertIn('already has an active sprint', str(serializer.errors['is_active']))
    
    def test_sprint_permission_validation(self):
        """Test only owners/managers can create sprints"""
        other_user = UserFactory()
        
        data = {
            'project_id': str(self.project.public_id),
            'name': 'Sprint 1',
            'goal': 'Complete MVP',
            'start_date': timezone.now().date(),
            'end_date': timezone.now().date() + timedelta(days=14)
        }
        
        serializer = SprintCreateUpdateSerializer(
            data=data,
            context={'request': self.get_request(other_user)}
        )
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('project_id', serializer.errors)
        self.assertIn("don't have permission", str(serializer.errors['project_id']))


class TaskSerializerTest(SerializerTestBase):
    """Test Task serializers"""
    
    def test_task_detail_serializer(self):
        """Test TaskDetailSerializer includes all relationships"""
        sprint = SprintFactory(project=self.project)
        task = TaskFactory(
            project=self.project,
            sprint=sprint,
            assignee=self.user
        )
        comment = CommentFactory(task=task)
        
        serializer = TaskDetailSerializer(task)
        data = serializer.data
        
        self.assertIn('project', data)
        self.assertIn('sprint', data)
        self.assertIn('assignee', data)
        self.assertIn('comments', data)
        self.assertEqual(len(data['comments']), 1)
    
    def test_task_create_valid_data(self):
        """Test creating task with valid data"""
        sprint = SprintFactory(project=self.project)
        assignee = UserFactory()
        ProjectMembershipFactory(project=self.project, user=assignee)
        
        data = {
            'title': 'New Task',
            'description': 'Task description',
            'assignee_id': str(assignee.public_id),
            'sprint_id': str(sprint.public_id),
            'status': 'todo',
            'priority': 'high',
            'story_points': 5
        }
        
        serializer = TaskCreateUpdateSerializer(
            data=data,
            context={'request': self.get_request()}
        )
        
        self.assertTrue(serializer.is_valid())
        task = serializer.save(project=self.project)
        
        self.assertEqual(task.title, 'New Task')
        self.assertEqual(task.assignee, assignee)
        self.assertEqual(task.sprint, sprint)
        self.assertEqual(task.created_by, self.user)
    
    def test_task_assignee_validation(self):
        """Test task assignee must exist"""
        data = {
            'title': 'New Task',
            'description': 'Task description',
            'assignee_id': '00000000-0000-0000-0000-000000000000',  # Invalid UUID
            'status': 'todo'
        }
        
        serializer = TaskCreateUpdateSerializer(
            data=data,
            context={'request': self.get_request()}
        )
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('assignee_id', serializer.errors)
        self.assertIn('Assignee not found', str(serializer.errors['assignee_id']))
    
    def test_task_sprint_validation(self):
        """Test task sprint must exist"""
        data = {
            'title': 'New Task',
            'description': 'Task description',
            'sprint_id': '00000000-0000-0000-0000-000000000000',  # Invalid UUID
            'status': 'todo'
        }
        
        serializer = TaskCreateUpdateSerializer(
            data=data,
            context={'request': self.get_request()}
        )
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('sprint_id', serializer.errors)
        self.assertIn('Sprint not found', str(serializer.errors['sprint_id']))
    
    def test_task_update_tracking(self):
        """Test task update tracking"""
        task = TaskFactory(project=self.project)
        
        data = {
            'title': 'Updated Task',
            'status': 'in_progress'
        }
        
        serializer = TaskCreateUpdateSerializer(
            instance=task,
            data=data,
            partial=True,
            context={'request': self.get_request()}
        )
        
        self.assertTrue(serializer.is_valid())
        updated_task = serializer.save()
        
        self.assertEqual(updated_task.title, 'Updated Task')
        self.assertEqual(updated_task.status, 'in_progress')
        self.assertEqual(updated_task.updated_by, self.user)


class CommentSerializerTest(SerializerTestBase):
    """Test Comment serializer"""
    
    def test_comment_serializer(self):
        """Test CommentSerializer with nested replies"""
        task = TaskFactory(project=self.project)
        parent_comment = CommentFactory(task=task, author=self.user)
        reply = CommentFactory(task=task, parent=parent_comment)
        
        serializer = CommentSerializer(parent_comment)
        data = serializer.data
        
        self.assertIn('replies', data)
        self.assertEqual(len(data['replies']), 1)
        self.assertEqual(data['replies'][0]['public_id'], str(reply.public_id))
    
    def test_comment_create(self):
        """Test creating comment"""
        task = TaskFactory(project=self.project)
        
        data = {
            'content': 'This is a comment'
        }
        
        serializer = CommentSerializer(
            data=data,
            context={'request': self.get_request()}
        )
        
        self.assertTrue(serializer.is_valid())
        comment = serializer.save(task=task)
        
        self.assertEqual(comment.content, 'This is a comment')
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.task, task)
    
    def test_comment_with_parent(self):
        """Test creating reply to comment"""
        task = TaskFactory(project=self.project)
        parent = CommentFactory(task=task)
        
        data = {
            'content': 'This is a reply',
            'parent': parent.public_id
        }
        
        serializer = CommentSerializer(
            data=data,
            context={'request': self.get_request()}
        )
        
        self.assertTrue(serializer.is_valid())
        reply = serializer.save(task=task)
        
        self.assertEqual(reply.parent, parent)


class ProjectMembershipSerializerTest(SerializerTestBase):
    """Test ProjectMembership serializer"""
    
    def test_membership_serializer(self):
        """Test ProjectMembershipSerializer"""
        membership = ProjectMembershipFactory(
            project=self.project,
            user=self.user,
            role='developer'
        )
        
        serializer = ProjectMembershipSerializer(membership)
        data = serializer.data
        
        self.assertIn('user', data)
        self.assertIn('role', data)
        self.assertIn('joined_at', data)
        self.assertEqual(data['role'], 'developer')
        
        # Check user summary is included
        self.assertIn('email', data['user'])
        self.assertIn('first_name', data['user'])
        self.assertIn('last_name', data['user'])
    
    def test_membership_user_validation(self):
        """Test membership user must exist"""
        data = {
            'user_id': '00000000-0000-0000-0000-000000000000',  # Invalid UUID
            'role': 'developer'
        }
        
        serializer = ProjectMembershipSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('user_id', serializer.errors)
        self.assertIn('User not found', str(serializer.errors['user_id']))