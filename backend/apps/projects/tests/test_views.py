"""
View/ViewSet tests for projects app
Ham Dog & TC's comprehensive API endpoint tests
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status

from apps.projects.models import Project, ProjectMembership, Sprint, Task, Comment
from .factories import (
    UserFactory, ProjectFactory, ProjectMembershipFactory,
    SprintFactory, TaskFactory, CommentFactory
)

User = get_user_model()


class APITestBase(TestCase):
    """Base class for API tests"""
    
    def setUp(self):
        self.client = APIClient()
        self.owner = UserFactory()
        self.manager = UserFactory()
        self.developer = UserFactory()
        self.outsider = UserFactory()
        
        # Create a project with team
        self.project = ProjectFactory(owner=self.owner)
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
    
    def authenticate(self, user):
        """Helper to authenticate a user"""
        self.client.force_authenticate(user=user)


class ProjectViewSetTest(APITestBase):
    """Test ProjectViewSet API endpoints"""
    
    def test_list_projects_for_owner(self):
        """Test owner can list their projects"""
        self.authenticate(self.owner)
        response = self.client.get('/api/v1/projects/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], self.project.name)
    
    def test_list_projects_for_member(self):
        """Test members can list projects they belong to"""
        self.authenticate(self.developer)
        response = self.client.get('/api/v1/projects/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_list_projects_excludes_non_members(self):
        """Test non-members cannot see projects"""
        self.authenticate(self.outsider)
        response = self.client.get('/api/v1/projects/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
    
    def test_create_project(self):
        """Test creating a new project"""
        self.authenticate(self.owner)
        data = {
            'name': 'New Project',
            'description': 'A new project',
            'status': 'planning',
            'start_date': timezone.now().date().isoformat(),
            'end_date': (timezone.now().date() + timedelta(days=30)).isoformat()
        }
        
        response = self.client.post('/api/v1/projects/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Project')
        
        # Check owner was added as member
        project = Project.objects.get(public_id=response.data['public_id'])
        self.assertTrue(
            ProjectMembership.objects.filter(
                project=project,
                user=self.owner,
                role='owner'
            ).exists()
        )
    
    def test_retrieve_project_as_member(self):
        """Test retrieving project details as a member"""
        self.authenticate(self.developer)
        response = self.client.get(f'/api/v1/projects/{self.project.public_id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.project.name)
        self.assertIn('memberships', response.data)
        self.assertIn('stats', response.data)
    
    def test_retrieve_project_denied_for_non_member(self):
        """Test non-members cannot retrieve project details"""
        self.authenticate(self.outsider)
        response = self.client.get(f'/api/v1/projects/{self.project.public_id}/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_project_as_owner(self):
        """Test owner can update project"""
        self.authenticate(self.owner)
        data = {'name': 'Updated Project Name'}
        
        response = self.client.patch(
            f'/api/v1/projects/{self.project.public_id}/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, 'Updated Project Name')
    
    def test_update_project_denied_for_member(self):
        """Test members cannot update project"""
        self.authenticate(self.developer)
        data = {'name': 'Hacked Name'}
        
        response = self.client.patch(
            f'/api/v1/projects/{self.project.public_id}/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_delete_project_as_owner(self):
        """Test owner can delete project"""
        self.authenticate(self.owner)
        response = self.client.delete(f'/api/v1/projects/{self.project.public_id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.project.refresh_from_db()
        self.assertTrue(self.project.is_deleted)
    
    def test_add_member_to_project(self):
        """Test adding a member to project"""
        self.authenticate(self.owner)
        new_user = UserFactory()
        
        data = {
            'user_id': str(new_user.public_id),
            'role': 'developer'
        }
        
        response = self.client.post(
            f'/api/v1/projects/{self.project.public_id}/add_member/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            ProjectMembership.objects.filter(
                project=self.project,
                user=new_user,
                role='developer'
            ).exists()
        )
    
    def test_cannot_add_duplicate_member(self):
        """Test cannot add same member twice"""
        self.authenticate(self.owner)
        
        data = {
            'user_id': str(self.developer.public_id),
            'role': 'developer'
        }
        
        response = self.client.post(
            f'/api/v1/projects/{self.project.public_id}/add_member/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already a project member', response.data['error'])
    
    def test_remove_member_from_project(self):
        """Test removing a member from project"""
        self.authenticate(self.owner)
        
        data = {'user_id': str(self.developer.public_id)}
        
        response = self.client.delete(
            f'/api/v1/projects/{self.project.public_id}/remove_member/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            ProjectMembership.objects.filter(
                project=self.project,
                user=self.developer
            ).exists()
        )
    
    def test_cannot_remove_owner(self):
        """Test cannot remove project owner"""
        self.authenticate(self.owner)
        # Add owner as explicit member
        owner_membership = ProjectMembershipFactory(
            project=self.project,
            user=self.owner,
            role='owner'
        )
        
        data = {'user_id': str(self.owner.public_id)}
        
        response = self.client.delete(
            f'/api/v1/projects/{self.project.public_id}/remove_member/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Cannot remove project owner', response.data['error'])
    
    def test_project_stats_endpoint(self):
        """Test project statistics endpoint"""
        # Create some tasks
        TaskFactory(project=self.project, status='done', story_points=5)
        TaskFactory(project=self.project, status='in_progress', story_points=3)
        TaskFactory(project=self.project, status='todo', story_points=8)
        
        self.authenticate(self.developer)
        response = self.client.get(f'/api/v1/projects/{self.project.public_id}/stats/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_tasks'], 3)
        self.assertEqual(response.data['tasks_by_status']['done'], 1)
        self.assertEqual(response.data['total_story_points'], 16)
        self.assertEqual(response.data['completed_story_points'], 5)


class SprintViewSetTest(APITestBase):
    """Test SprintViewSet API endpoints"""
    
    def setUp(self):
        super().setUp()
        self.sprint = SprintFactory(project=self.project)
    
    def test_list_sprints(self):
        """Test listing sprints for a project"""
        self.authenticate(self.developer)
        response = self.client.get(
            '/api/v1/sprints/',
            {'project': str(self.project.public_id)}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_sprint_as_manager(self):
        """Test manager can create sprints"""
        self.authenticate(self.manager)
        
        data = {
            'project_id': str(self.project.public_id),
            'name': 'Sprint 2',
            'goal': 'Complete features',
            'start_date': timezone.now().date().isoformat(),
            'end_date': (timezone.now().date() + timedelta(days=14)).isoformat()
        }
        
        response = self.client.post('/api/v1/sprints/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Sprint 2')
    
    def test_create_sprint_denied_for_developer(self):
        """Test developer cannot create sprints"""
        self.authenticate(self.developer)
        
        data = {
            'project_id': str(self.project.public_id),
            'name': 'Sprint 2',
            'goal': 'Complete features',
            'start_date': timezone.now().date().isoformat(),
            'end_date': (timezone.now().date() + timedelta(days=14)).isoformat()
        }
        
        response = self.client.post('/api/v1/sprints/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_activate_sprint(self):
        """Test activating a sprint"""
        self.authenticate(self.manager)
        
        response = self.client.post(
            f'/api/v1/sprints/{self.sprint.public_id}/activate/'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.sprint.refresh_from_db()
        self.assertTrue(self.sprint.is_active)
    
    def test_only_one_active_sprint(self):
        """Test only one sprint can be active per project"""
        sprint1 = SprintFactory(project=self.project, is_active=True)
        sprint2 = SprintFactory(project=self.project, is_active=False)
        
        self.authenticate(self.owner)
        
        response = self.client.post(
            f'/api/v1/sprints/{sprint2.public_id}/activate/'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        sprint1.refresh_from_db()
        sprint2.refresh_from_db()
        
        self.assertFalse(sprint1.is_active)
        self.assertTrue(sprint2.is_active)


class TaskViewSetTest(APITestBase):
    """Test TaskViewSet API endpoints"""
    
    def setUp(self):
        super().setUp()
        self.task = TaskFactory(
            project=self.project,
            assignee=self.developer
        )
    
    def test_list_tasks(self):
        """Test listing tasks for a project"""
        self.authenticate(self.developer)
        response = self.client.get(
            '/api/v1/tasks/',
            {'project': str(self.project.public_id)}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_task(self):
        """Test creating a task"""
        self.authenticate(self.manager)
        
        data = {
            'project_id': str(self.project.public_id),
            'title': 'New Task',
            'description': 'Task description',
            'status': 'todo',
            'priority': 'medium',
            'story_points': 5
        }
        
        response = self.client.post('/api/v1/tasks/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Task')
    
    def test_update_task_as_assignee(self):
        """Test assignee can update their task"""
        self.authenticate(self.developer)
        
        data = {'status': 'in_progress'}
        
        response = self.client.patch(
            f'/api/v1/tasks/{self.task.public_id}/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'in_progress')
    
    def test_update_task_denied_for_non_assignee(self):
        """Test non-assignee developer cannot update task"""
        other_developer = UserFactory()
        ProjectMembershipFactory(
            project=self.project,
            user=other_developer,
            role='developer'
        )
        
        self.authenticate(other_developer)
        
        data = {'status': 'done'}
        
        response = self.client.patch(
            f'/api/v1/tasks/{self.task.public_id}/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_quick_status_update(self):
        """Test quick status update endpoint"""
        self.authenticate(self.developer)
        
        data = {'status': 'done'}
        
        response = self.client.patch(
            f'/api/v1/tasks/{self.task.public_id}/update_status/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'done')
    
    def test_add_comment_to_task(self):
        """Test adding a comment to a task"""
        self.authenticate(self.developer)
        
        data = {'content': 'This is a comment'}
        
        response = self.client.post(
            f'/api/v1/tasks/{self.task.public_id}/add_comment/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'This is a comment')
        
        # Check comment was created
        self.assertEqual(self.task.comments.count(), 1)
    
    def test_delete_task_as_manager(self):
        """Test manager can delete tasks"""
        self.authenticate(self.manager)
        
        response = self.client.delete(f'/api/v1/tasks/{self.task.public_id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.task.refresh_from_db()
        self.assertTrue(self.task.is_deleted)


class CommentViewSetTest(APITestBase):
    """Test CommentViewSet API endpoints"""
    
    def setUp(self):
        super().setUp()
        self.task = TaskFactory(project=self.project)
        self.comment = CommentFactory(
            task=self.task,
            author=self.developer
        )
    
    def test_list_comments(self):
        """Test listing comments for project members"""
        self.authenticate(self.developer)
        response = self.client.get('/api/v1/comments/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_update_comment_as_author(self):
        """Test author can update their comment"""
        self.authenticate(self.developer)
        
        data = {'content': 'Updated comment'}
        
        response = self.client.patch(
            f'/api/v1/comments/{self.comment.public_id}/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, 'Updated comment')
        self.assertTrue(self.comment.edited)
    
    def test_update_comment_denied_for_non_author(self):
        """Test non-author cannot update comment"""
        other_developer = UserFactory()
        ProjectMembershipFactory(
            project=self.project,
            user=other_developer,
            role='developer'
        )
        
        self.authenticate(other_developer)
        
        data = {'content': 'Hacked comment'}
        
        response = self.client.patch(
            f'/api/v1/comments/{self.comment.public_id}/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_delete_comment_as_author(self):
        """Test author can delete their comment"""
        self.authenticate(self.developer)
        
        response = self.client.delete(
            f'/api/v1/comments/{self.comment.public_id}/'
        )
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())
    
    def test_manager_can_moderate_comments(self):
        """Test manager can delete any comment"""
        self.authenticate(self.manager)
        
        response = self.client.delete(
            f'/api/v1/comments/{self.comment.public_id}/'
        )
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())