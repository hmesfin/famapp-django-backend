"""
Factory classes for projects app testing
Ham Dog & TC's test data generators
"""
import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from apps.projects.models import (
    Project, ProjectMembership, Sprint, Task, Comment
)

User = get_user_model()


class UserFactory(DjangoModelFactory):
    """Factory for creating test users"""
    class Meta:
        model = User
        django_get_or_create = ('email',)
    
    email = factory.Sequence(lambda n: f'user{n}@test.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True
    
    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            self.set_password(extracted)
        else:
            self.set_password('testpass123')


class ProjectFactory(DjangoModelFactory):
    """Factory for creating test projects"""
    class Meta:
        model = Project
    
    name = factory.Sequence(lambda n: f'Project {n}')
    slug = factory.LazyAttribute(lambda obj: obj.name.lower().replace(' ', '-'))
    description = factory.Faker('text', max_nb_chars=200)
    status = 'active'
    owner = factory.SubFactory(UserFactory)
    created_by = factory.LazyAttribute(lambda obj: obj.owner)
    start_date = factory.LazyFunction(timezone.now)
    end_date = factory.LazyFunction(lambda: timezone.now() + timedelta(days=90))


class ProjectMembershipFactory(DjangoModelFactory):
    """Factory for creating project memberships"""
    class Meta:
        model = ProjectMembership
        django_get_or_create = ('project', 'user')
    
    project = factory.SubFactory(ProjectFactory)
    user = factory.SubFactory(UserFactory)
    role = 'developer'
    joined_at = factory.LazyFunction(timezone.now)


class SprintFactory(DjangoModelFactory):
    """Factory for creating test sprints"""
    class Meta:
        model = Sprint
    
    project = factory.SubFactory(ProjectFactory)
    name = factory.Sequence(lambda n: f'Sprint {n}')
    goal = factory.Faker('sentence', nb_words=10)
    start_date = factory.LazyFunction(lambda: timezone.now().date())
    end_date = factory.LazyFunction(lambda: (timezone.now() + timedelta(days=14)).date())
    is_active = False


class TaskFactory(DjangoModelFactory):
    """Factory for creating test tasks"""
    class Meta:
        model = Task
    
    project = factory.SubFactory(ProjectFactory)
    sprint = factory.SubFactory(SprintFactory, project=factory.SelfAttribute('..project'))
    title = factory.Faker('sentence', nb_words=6)
    description = factory.Faker('text', max_nb_chars=500)
    assignee = factory.SubFactory(UserFactory)
    status = 'todo'
    priority = 'medium'
    story_points = factory.Faker('random_int', min=1, max=13)
    due_date = factory.LazyFunction(lambda: timezone.now() + timedelta(days=7))
    created_by = factory.LazyAttribute(lambda obj: obj.project.owner)


class CommentFactory(DjangoModelFactory):
    """Factory for creating test comments"""
    class Meta:
        model = Comment
    
    task = factory.SubFactory(TaskFactory)
    content = factory.Faker('text', max_nb_chars=200)
    author = factory.SubFactory(UserFactory)
    parent = None
    edited = False