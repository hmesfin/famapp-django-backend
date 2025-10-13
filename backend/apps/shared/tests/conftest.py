"""
Fixtures for shared app tests
"""

import pytest
from django.contrib.auth import get_user_model
from django.db import connection
from django.db.models import CharField

from apps.shared.models import BaseModel
from apps.shared.models import SimpleBaseModel

User = get_user_model()


# Create concrete test models dynamically
class TestBaseModelConcrete(BaseModel):
    """Concrete model for testing BaseModel"""

    name = CharField(max_length=100)

    class Meta:
        app_label = "shared"
        db_table = "test_base_model_concrete"


class TestSimpleBaseModelConcrete(SimpleBaseModel):
    """Concrete model for testing SimpleBaseModel"""

    title = CharField(max_length=100)

    class Meta:
        app_label = "shared"
        db_table = "test_simple_base_model_concrete"


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """Create test model tables in the database"""
    with django_db_blocker.unblock():
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(TestBaseModelConcrete)
            schema_editor.create_model(TestSimpleBaseModelConcrete)

    yield

    # Cleanup after all tests
    with django_db_blocker.unblock():
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(TestSimpleBaseModelConcrete)
            schema_editor.delete_model(TestBaseModelConcrete)


@pytest.fixture
def user(db):
    """Create a test user"""
    return User.objects.create_user(
        email="test@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def admin_user(db):
    """Create an admin user"""
    return User.objects.create_superuser(
        email="admin@example.com", password="adminpass123",
    )


# FamApp model fixtures
@pytest.fixture
def family(db, user):
    """Create a test family"""
    from apps.shared.models import Family
    from apps.shared.models import FamilyMember

    family = Family.objects.create(name="Test Family", created_by=user)
    FamilyMember.objects.create(
        family=family, user=user, role=FamilyMember.Role.ORGANIZER,
    )
    return family


@pytest.fixture
def todo(db, user, family):
    """Create a test todo"""
    from apps.shared.models import Todo

    return Todo.objects.create(
        family=family,
        title="Test Todo",
        description="Test description",
        assigned_to=user,
        created_by=user,
    )


@pytest.fixture
def schedule_event(db, user, family):
    """Create a test schedule event"""
    from datetime import timedelta

    from django.utils import timezone

    from apps.shared.models import ScheduleEvent

    start_time = timezone.now() + timedelta(days=1)
    end_time = start_time + timedelta(hours=2)

    return ScheduleEvent.objects.create(
        family=family,
        title="Test Event",
        description="Test event description",
        start_time=start_time,
        end_time=end_time,
        location="Test Location",
        created_by=user,
    )


@pytest.fixture
def grocery_item(db, user, family):
    """Create a test grocery item"""
    from apps.shared.models import GroceryItem

    return GroceryItem.objects.create(
        family=family,
        name="Test Grocery",
        quantity=2,
        unit="pieces",
        created_by=user,
    )


@pytest.fixture
def pet(db, user, family):
    """Create a test pet"""
    from apps.shared.models import Pet

    return Pet.objects.create(
        family=family,
        name="Fluffy",
        species="dog",
        breed="Golden Retriever",
        age=4,
        created_by=user,
    )
