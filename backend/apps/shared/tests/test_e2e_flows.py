"""
End-to-End Test Suite for FamApp Critical User Flows.

Tests verify complete user journeys from signup to feature usage:
- User registration → Family creation → Todo management
- Family invitation → Member acceptance → Shared data access
- Pet activity logging → Last activity timestamps
- Event creation → Event listing

Ham Dog & TC testing the full stack! 🔮
"""

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.shared.models import Family
from apps.shared.models import FamilyMember
from apps.shared.models import GroceryItem
from apps.shared.models import Pet
from apps.shared.models import PetActivity
from apps.shared.models import ScheduleEvent
from apps.shared.models import Todo

User = get_user_model()


@pytest.mark.django_db
class TestUserSignupAndTodoFlow:
    """
    E2E Test: User Signup → Create Family → Add Todo → Complete Todo.

    This test verifies the most critical user journey in FamApp:
    1. New user signs up
    2. User creates their first family
    3. User adds a todo to the family
    4. User completes the todo
    """

    def test_complete_signup_and_todo_flow(self):
        """Test full flow: signup → create family → add todo → complete todo."""
        client = APIClient()

        # Step 1: User signs up
        signup_data = {
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "first_name": "New",
            "last_name": "User",
        }
        signup_response = client.post("/api/auth/register/", signup_data)
        assert signup_response.status_code == status.HTTP_201_CREATED
        assert "user" in signup_response.data
        assert signup_response.data["user"]["email"] == "newuser@example.com"

        # Mark user as email verified (simulating email verification)
        user = User.objects.get(email="newuser@example.com")
        user.email_verified = True
        user.save()

        # Step 1b: User logs in to get JWT tokens
        login_data = {
            "email": "newuser@example.com",
            "password": "SecurePass123!",
        }
        login_response = client.post("/api/auth/login/", login_data)
        assert login_response.status_code == status.HTTP_200_OK
        assert "access" in login_response.data
        assert "refresh" in login_response.data

        # Authenticate for subsequent requests
        access_token = login_response.data["access"]
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        # Verify user was created
        user = User.objects.get(email="newuser@example.com")
        assert user.first_name == "New"
        assert user.last_name == "User"

        # Step 2: User creates their first family
        family_data = {"name": "My New Family"}
        family_response = client.post("/api/v1/families/", family_data)
        assert family_response.status_code == status.HTTP_201_CREATED
        assert family_response.data["name"] == "My New Family"

        family_public_id = family_response.data["public_id"]

        # Verify family was created with user as organizer
        family = Family.objects.get(public_id=family_public_id)
        assert family.created_by == user
        membership = FamilyMember.objects.get(family=family, user=user)
        assert membership.role == FamilyMember.Role.ORGANIZER

        # Step 3: User adds a todo to the family
        todo_data = {
            "family_public_id": family_public_id,
            "title": "Buy groceries",
            "description": "Get milk, eggs, and bread",
            "status": "todo",
        }
        todo_response = client.post(
            "/api/v1/todos/",
            todo_data,
        )
        assert todo_response.status_code == status.HTTP_201_CREATED
        assert todo_response.data["title"] == "Buy groceries"
        assert todo_response.data["status"] == "todo"

        todo_public_id = todo_response.data["public_id"]

        # Verify todo was created
        todo = Todo.objects.get(public_id=todo_public_id)
        assert todo.family == family
        assert todo.created_by == user

        # Step 4: User completes the todo
        complete_data = {"status": "done"}
        complete_response = client.patch(
            f"/api/v1/todos/{todo_public_id}/",
            complete_data,
        )
        assert complete_response.status_code == status.HTTP_200_OK
        assert complete_response.data["status"] == "done"

        # Verify todo was marked as done
        todo.refresh_from_db()
        assert todo.status == Todo.Status.DONE

        # Step 5: User can retrieve their todos
        list_response = client.get("/api/v1/todos/")
        assert list_response.status_code == status.HTTP_200_OK
        assert len(list_response.data["results"]) == 1
        assert list_response.data["results"][0]["status"] == "done"


@pytest.mark.django_db
class TestInvitationFlow:
    """
    E2E Test: Invite Member → Accept Invitation → View Shared Data.

    This test verifies the family invitation and data sharing flow:
    1. Organizer creates family with todos
    2. Organizer invites new member
    3. New member accepts invitation
    4. New member can view shared family data
    """

    def test_complete_invitation_flow(self):
        """Test full flow: invite → accept → view shared data."""
        client = APIClient()

        # Setup: Create organizer and family with data
        organizer = User.objects.create_user(
            email="organizer@example.com",
            password="OrgPass123!",
            first_name="Org",
            last_name="Anizer",
        )
        family = Family.objects.create(name="Test Family", created_by=organizer)
        FamilyMember.objects.create(
            family=family,
            user=organizer,
            role=FamilyMember.Role.ORGANIZER,
        )

        # Create some shared data (todo)
        todo = Todo.objects.create(
            family=family,
            title="Shared Todo",
            description="Everyone can see this",
            status=Todo.Status.TODO,
            created_by=organizer,
        )

        # Step 1: Organizer invites new member
        client.force_authenticate(user=organizer)
        invite_data = {
            "email": "newmember@example.com",
            "role": "member",
        }
        invite_response = client.post(
            f"/api/v1/families/" + str(family.public_id) + "/invite/",
            invite_data,
        )
        assert invite_response.status_code == status.HTTP_201_CREATED

        # Step 2: New member signs up
        client.credentials()  # Clear authentication
        signup_data = {
            "email": "newmember@example.com",
            "password": "MemberPass123!",
            "password_confirm": "MemberPass123!",
            "first_name": "New",
            "last_name": "Member",
        }
        signup_response = client.post("/api/auth/register/", signup_data)
        assert signup_response.status_code == status.HTTP_201_CREATED

        # Mark new member as email verified (simulating email verification)
        new_member = User.objects.get(email="newmember@example.com")
        new_member.email_verified = True
        new_member.save()

        # Step 2b: New member logs in to get JWT tokens
        login_data = {
            "email": "newmember@example.com",
            "password": "MemberPass123!",
        }
        login_response = client.post("/api/auth/login/", login_data)
        assert login_response.status_code == status.HTTP_200_OK

        access_token = login_response.data["access"]
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        # Step 3: New member accepts invitation
        accept_response = client.post(
            f"/api/v1/families/" + str(family.public_id) + "/invitations/accept/",
        )
        assert accept_response.status_code == status.HTTP_200_OK

        # Verify membership was created
        membership = FamilyMember.objects.get(family=family, user=new_member)
        assert membership.role == FamilyMember.Role.MEMBER

        # Step 4: New member can view shared family data
        family_response = client.get(f"/api/v1/families/{family.public_id}/")
        assert family_response.status_code == status.HTTP_200_OK
        assert family_response.data["name"] == "Test Family"

        # Step 5: New member can view shared todos
        todo_response = client.get("/api/v1/todos/")
        assert todo_response.status_code == status.HTTP_200_OK
        assert len(todo_response.data["results"]) == 1
        assert todo_response.data["results"][0]["title"] == "Shared Todo"

        # Step 6: New member can update the shared todo
        update_data = {"status": "in_progress"}
        update_response = client.patch(
            f"/api/v1/todos/{todo.public_id}/",
            update_data,
        )
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.data["status"] == "in_progress"


@pytest.mark.django_db
class TestPetActivityFlow:
    """
    E2E Test: Log Pet Activity → Verify Last Activity Timestamps.

    This test verifies pet activity tracking works correctly:
    1. Create family with pet
    2. Log feeding activity
    3. Verify last_fed_at timestamp
    4. Log walking activity
    5. Verify last_walked_at timestamp
    """

    def test_complete_pet_activity_flow(self):
        """Test full flow: log activities → verify timestamps."""
        client = APIClient()

        # Setup: Create user, family, and pet
        user = User.objects.create_user(
            email="petowner@example.com",
            password="PetPass123!",
            first_name="Pet",
            last_name="Owner",
        )
        family = Family.objects.create(name="Pet Family", created_by=user)
        FamilyMember.objects.create(
            family=family,
            user=user,
            role=FamilyMember.Role.ORGANIZER,
        )

        client.force_authenticate(user=user)

        # Step 1: Create a pet
        pet_data = {
            "family_public_id": str(family.public_id),
            "name": "Buddy",
            "species": "dog",
            "breed": "Golden Retriever",
            "age": 3,
        }
        pet_response = client.post(
            f"/api/v1/pets/",
            pet_data,
        )
        assert pet_response.status_code == status.HTTP_201_CREATED
        assert pet_response.data["name"] == "Buddy"
        assert pet_response.data["last_fed_at"] is None
        assert pet_response.data["last_walked_at"] is None

        pet_public_id = pet_response.data["public_id"]
        pet = Pet.objects.get(public_id=pet_public_id)

        # Step 2: Log feeding activity
        feeding_time = timezone.now()
        feeding_data = {
            "activity_type": "feeding",
            "scheduled_time": feeding_time.isoformat(),
            "is_completed": True,
            "completed_at": feeding_time.isoformat(),
            "notes": "Fed with kibble",
        }
        feeding_response = client.post(
            f"/api/v1/pets/{pet_public_id}/activities/",
            feeding_data,
        )
        assert feeding_response.status_code == status.HTTP_201_CREATED
        assert feeding_response.data["activity_type"] == "feeding"
        assert feeding_response.data["is_completed"] is True

        # Step 3: Verify last_fed_at timestamp was updated
        pet_detail_response = client.get(
            f"/api/v1/pets/{pet_public_id}/",
        )
        assert pet_detail_response.status_code == status.HTTP_200_OK
        assert pet_detail_response.data["last_fed_at"] is not None
        assert pet_detail_response.data["last_walked_at"] is None

        # Verify in database
        pet.refresh_from_db()
        assert pet.last_fed_at is not None
        assert pet.last_walked_at is None

        # Step 4: Log walking activity
        walking_time = timezone.now()
        walking_data = {
            "activity_type": "walking",
            "scheduled_time": walking_time.isoformat(),
            "is_completed": True,
            "completed_at": walking_time.isoformat(),
            "notes": "30 minute walk in the park",
        }
        walking_response = client.post(
            f"/api/v1/pets/{pet_public_id}/activities/",
            walking_data,
        )
        assert walking_response.status_code == status.HTTP_201_CREATED
        assert walking_response.data["activity_type"] == "walking"
        assert walking_response.data["is_completed"] is True

        # Step 5: Verify last_walked_at timestamp was updated
        pet_detail_response = client.get(
            f"/api/v1/pets/{pet_public_id}/",
        )
        assert pet_detail_response.status_code == status.HTTP_200_OK
        assert pet_detail_response.data["last_fed_at"] is not None
        assert pet_detail_response.data["last_walked_at"] is not None

        # Verify in database
        pet.refresh_from_db()
        assert pet.last_fed_at is not None
        assert pet.last_walked_at is not None

        # Step 6: Verify activities appear in list
        activities_response = client.get(
            f"/api/v1/pets/{pet_public_id}/activities/",
        )
        assert activities_response.status_code == status.HTTP_200_OK
        assert len(activities_response.data["results"]) == 2


@pytest.mark.django_db
class TestEventCreationFlow:
    """
    E2E Test: Create Event → Verify Event Appears in List.

    This test verifies event creation and listing works correctly:
    1. Create family
    2. Create multiple events
    3. Verify events appear in list
    4. Verify event filtering by date
    """

    def test_complete_event_creation_flow(self):
        """Test full flow: create events → verify listing."""
        client = APIClient()

        # Setup: Create user and family
        user = User.objects.create_user(
            email="eventplanner@example.com",
            password="EventPass123!",
            first_name="Event",
            last_name="Planner",
        )
        family = Family.objects.create(name="Event Family", created_by=user)
        FamilyMember.objects.create(
            family=family,
            user=user,
            role=FamilyMember.Role.ORGANIZER,
        )

        client.force_authenticate(user=user)

        # Step 1: Create first event (upcoming)
        start_time = timezone.now() + timezone.timedelta(days=1)
        end_time = start_time + timezone.timedelta(hours=2)
        event1_data = {
            "family_public_id": str(family.public_id),
            "title": "Family Dinner",
            "description": "Monthly family dinner at our place",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "location": "Home",
        }
        event1_response = client.post(
            f"/api/v1/events/",
            event1_data,
        )
        assert event1_response.status_code == status.HTTP_201_CREATED
        assert event1_response.data["title"] == "Family Dinner"

        # Step 2: Create second event (further in future)
        start_time2 = timezone.now() + timezone.timedelta(days=7)
        end_time2 = start_time2 + timezone.timedelta(hours=3)
        event2_data = {
            "family_public_id": str(family.public_id),
            "title": "Weekend Trip",
            "description": "Family trip to the mountains",
            "start_time": start_time2.isoformat(),
            "end_time": end_time2.isoformat(),
            "location": "Mountain Resort",
        }
        event2_response = client.post(
            f"/api/v1/events/",
            event2_data,
        )
        assert event2_response.status_code == status.HTTP_201_CREATED
        assert event2_response.data["title"] == "Weekend Trip"

        # Step 3: Verify both events appear in list
        events_response = client.get(f"/api/v1/events/")
        assert events_response.status_code == status.HTTP_200_OK
        assert len(events_response.data["results"]) == 2

        # Events should be ordered by start_time
        results = events_response.data["results"]
        assert results[0]["title"] == "Family Dinner"
        assert results[1]["title"] == "Weekend Trip"

        # Step 4: Verify can retrieve individual event
        event1_public_id = event1_response.data["public_id"]
        detail_response = client.get(
            f"/api/v1/events/{event1_public_id}/",
        )
        assert detail_response.status_code == status.HTTP_200_OK
        assert detail_response.data["title"] == "Family Dinner"
        assert detail_response.data["location"] == "Home"

        # Step 5: Verify can update event
        update_data = {"location": "Restaurant"}
        update_response = client.patch(
            f"/api/v1/events/{event1_public_id}/",
            update_data,
        )
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.data["location"] == "Restaurant"

        # Verify in database
        event = ScheduleEvent.objects.get(public_id=event1_public_id)
        assert event.location == "Restaurant"


@pytest.mark.django_db
class TestGroceryShoppingFlow:
    """
    E2E Test: Add Grocery Items → Mark as Purchased → Remove from List.

    This test verifies grocery list management:
    1. Create family
    2. Add multiple grocery items
    3. Mark items as purchased
    4. Remove purchased items
    """

    def test_complete_grocery_shopping_flow(self):
        """Test full flow: add items → mark purchased → remove."""
        client = APIClient()

        # Setup: Create user and family
        user = User.objects.create_user(
            email="shopper@example.com",
            password="ShopPass123!",
            first_name="Grocery",
            last_name="Shopper",
        )
        family = Family.objects.create(name="Shopping Family", created_by=user)
        FamilyMember.objects.create(
            family=family,
            user=user,
            role=FamilyMember.Role.ORGANIZER,
        )

        client.force_authenticate(user=user)

        # Step 1: Add grocery items
        items_data = [
            {"family_public_id": str(family.public_id), "name": "Milk", "quantity": 2, "unit": "gallons"},
            {"family_public_id": str(family.public_id), "name": "Eggs", "quantity": 12, "unit": "pieces"},
            {"family_public_id": str(family.public_id), "name": "Bread", "quantity": 1, "unit": "loaf"},
        ]

        created_items = []
        for item_data in items_data:
            response = client.post(
                f"/api/v1/groceries/",
                item_data,
            )
            assert response.status_code == status.HTTP_201_CREATED
            created_items.append(response.data)

        # Step 2: Verify all items appear in list
        list_response = client.get(f"/api/v1/groceries/")
        assert list_response.status_code == status.HTTP_200_OK
        assert len(list_response.data["results"]) == 3

        # All items should be unpurchased by default
        for item in list_response.data["results"]:
            assert item["is_purchased"] is False

        # Step 3: Mark milk as purchased
        milk_public_id = created_items[0]["public_id"]
        purchase_data = {"is_purchased": True}
        purchase_response = client.patch(
            f"/api/v1/groceries/{milk_public_id}/",
            purchase_data,
        )
        assert purchase_response.status_code == status.HTTP_200_OK
        assert purchase_response.data["is_purchased"] is True

        # Verify in database
        milk = GroceryItem.objects.get(public_id=milk_public_id)
        assert milk.is_purchased is True
        assert milk.purchased_at is not None

        # Step 4: Filter purchased vs unpurchased items
        unpurchased_response = client.get(
            f"/api/v1/groceries/?is_purchased=false",
        )
        assert unpurchased_response.status_code == status.HTTP_200_OK
        assert len(unpurchased_response.data["results"]) == 2

        purchased_response = client.get(
            f"/api/v1/groceries/?is_purchased=true",
        )
        assert purchased_response.status_code == status.HTTP_200_OK
        assert len(purchased_response.data["results"]) == 1

        # Step 5: Soft delete purchased item
        delete_response = client.delete(
            f"/api/v1/groceries/{milk_public_id}/",
        )
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        # Verify item is soft deleted
        milk.refresh_from_db()
        assert milk.is_deleted is True

        # Step 6: Verify item no longer appears in list
        final_list_response = client.get(
            f"/api/v1/groceries/",
        )
        assert final_list_response.status_code == status.HTTP_200_OK
        assert len(final_list_response.data["results"]) == 2
