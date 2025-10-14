"""
Tests for Django admin interfaces.
"""

from django.contrib import admin
from django.test import TestCase

from apps.shared.models import Family
from apps.shared.models import FamilyMember
from apps.shared.models import GroceryItem
from apps.shared.models import Pet
from apps.shared.models import PetActivity
from apps.shared.models import ScheduleEvent
from apps.shared.models import Todo


class AdminRegistrationTests(TestCase):
    """Test that all models are registered in Django admin."""

    def test_family_registered(self):
        """Test Family model is registered in admin."""
        self.assertIn(Family, admin.site._registry)

    def test_family_member_registered(self):
        """Test FamilyMember model is registered in admin."""
        self.assertIn(FamilyMember, admin.site._registry)

    def test_todo_registered(self):
        """Test Todo model is registered in admin."""
        self.assertIn(Todo, admin.site._registry)

    def test_schedule_event_registered(self):
        """Test ScheduleEvent model is registered in admin."""
        self.assertIn(ScheduleEvent, admin.site._registry)

    def test_grocery_item_registered(self):
        """Test GroceryItem model is registered in admin."""
        self.assertIn(GroceryItem, admin.site._registry)

    def test_pet_registered(self):
        """Test Pet model is registered in admin."""
        self.assertIn(Pet, admin.site._registry)

    def test_pet_activity_registered(self):
        """Test PetActivity model is registered in admin."""
        self.assertIn(PetActivity, admin.site._registry)


class FamilyAdminTests(TestCase):
    """Test Family admin configuration."""

    def test_family_admin_list_display(self):
        """Test Family admin has proper list_display."""
        admin_class = admin.site._registry[Family]
        self.assertIn("name", admin_class.list_display)
        self.assertIn("created_at", admin_class.list_display)

    def test_family_admin_search_fields(self):
        """Test Family admin has search fields."""
        admin_class = admin.site._registry[Family]
        self.assertTrue(len(admin_class.search_fields) > 0)

    def test_family_admin_list_filter(self):
        """Test Family admin has list filters."""
        admin_class = admin.site._registry[Family]
        self.assertIn("created_at", admin_class.list_filter)


class TodoAdminTests(TestCase):
    """Test Todo admin configuration."""

    def test_todo_admin_list_display(self):
        """Test Todo admin has proper list_display."""
        admin_class = admin.site._registry[Todo]
        self.assertIn("title", admin_class.list_display)
        self.assertIn("status", admin_class.list_display)
        self.assertIn("priority", admin_class.list_display)

    def test_todo_admin_list_filter(self):
        """Test Todo admin has list filters."""
        admin_class = admin.site._registry[Todo]
        self.assertIn("status", admin_class.list_filter)
        self.assertIn("priority", admin_class.list_filter)


class ScheduleEventAdminTests(TestCase):
    """Test ScheduleEvent admin configuration."""

    def test_event_admin_list_display(self):
        """Test ScheduleEvent admin has proper list_display."""
        admin_class = admin.site._registry[ScheduleEvent]
        self.assertIn("title", admin_class.list_display)
        self.assertIn("start_time", admin_class.list_display)
        self.assertIn("end_time", admin_class.list_display)


class GroceryItemAdminTests(TestCase):
    """Test GroceryItem admin configuration."""

    def test_grocery_admin_list_display(self):
        """Test GroceryItem admin has proper list_display."""
        admin_class = admin.site._registry[GroceryItem]
        self.assertIn("name", admin_class.list_display)
        self.assertIn("is_purchased", admin_class.list_display)

    def test_grocery_admin_list_filter(self):
        """Test GroceryItem admin has list filters."""
        admin_class = admin.site._registry[GroceryItem]
        self.assertIn("is_purchased", admin_class.list_filter)


class PetAdminTests(TestCase):
    """Test Pet admin configuration."""

    def test_pet_admin_list_display(self):
        """Test Pet admin has proper list_display."""
        admin_class = admin.site._registry[Pet]
        self.assertIn("name", admin_class.list_display)
        self.assertIn("species", admin_class.list_display)


class PetActivityAdminTests(TestCase):
    """Test PetActivity admin configuration."""

    def test_pet_activity_admin_list_display(self):
        """Test PetActivity admin has proper list_display."""
        admin_class = admin.site._registry[PetActivity]
        self.assertIn("pet", admin_class.list_display)
        self.assertIn("activity_type", admin_class.list_display)
        self.assertIn("is_completed", admin_class.list_display)
