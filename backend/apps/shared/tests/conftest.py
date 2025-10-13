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
        email="admin@example.com", password="adminpass123"
    )
