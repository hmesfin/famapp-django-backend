"""
Manual test script for cleanup_expired_invitations task.
Run this in Django shell: docker compose run --rm django python manage.py shell < test_cleanup_task.py
"""

from django.utils import timezone
from datetime import timedelta
from apps.users.models import User, Invitation
from apps.shared.models import Family, FamilyMember
from apps.users.tasks import cleanup_expired_invitations

print("\n" + "="*60)
print("MANUAL TEST: cleanup_expired_invitations task")
print("="*60)

# Create test data
print("\n1. Creating test data...")

# Create inviter user
inviter = User.objects.create_user(
    email="test_inviter@example.com",
    password="testpass123",
    first_name="Test",
    last_name="Inviter"
)

# Create family
family = Family.objects.create(
    name="Test Family for Cleanup",
    created_by=inviter
)
FamilyMember.objects.create(
    family=family,
    user=inviter,
    role=FamilyMember.Role.ORGANIZER
)

# Create various invitations for testing
invitations = []

# 1. Expired PENDING invitation (should be marked EXPIRED)
inv1 = Invitation.objects.create(
    family=family,
    inviter=inviter,
    invitee_email="expired_pending@example.com",
    role=Invitation.Role.PARENT,
    status=Invitation.Status.PENDING,
    expires_at=timezone.now() - timedelta(days=2)
)
invitations.append(("Expired PENDING", inv1))

# 2. Future PENDING invitation (should NOT be changed)
inv2 = Invitation.objects.create(
    family=family,
    inviter=inviter,
    invitee_email="future_pending@example.com",
    role=Invitation.Role.CHILD,
    status=Invitation.Status.PENDING,
    expires_at=timezone.now() + timedelta(days=5)
)
invitations.append(("Future PENDING", inv2))

# 3. Expired ACCEPTED invitation (should NOT be changed)
inv3 = Invitation.objects.create(
    family=family,
    inviter=inviter,
    invitee_email="expired_accepted@example.com",
    role=Invitation.Role.PARENT,
    status=Invitation.Status.ACCEPTED,
    expires_at=timezone.now() - timedelta(days=3)
)
invitations.append(("Expired ACCEPTED", inv3))

# 4. Another expired PENDING invitation
inv4 = Invitation.objects.create(
    family=family,
    inviter=inviter,
    invitee_email="another_expired@example.com",
    role=Invitation.Role.CHILD,
    status=Invitation.Status.PENDING,
    expires_at=timezone.now() - timedelta(hours=12)
)
invitations.append(("Another Expired PENDING", inv4))

print("\n2. Initial invitation statuses:")
print("-" * 40)
for label, inv in invitations:
    print(f"{label:25} | Status: {inv.status:10} | Expired: {inv.is_expired}")

print("\n3. Running cleanup_expired_invitations task...")
print("-" * 40)

# Run the cleanup task
result = cleanup_expired_invitations.apply()
print(f"Task result: {result.result}")

print("\n4. After cleanup - invitation statuses:")
print("-" * 40)
for label, inv in invitations:
    inv.refresh_from_db()
    print(f"{label:25} | Status: {inv.status:10} | Expired: {inv.is_expired}")

print("\n5. Verification:")
print("-" * 40)

# Verify results
expected_results = [
    ("Expired PENDING", Invitation.Status.EXPIRED),
    ("Future PENDING", Invitation.Status.PENDING),
    ("Expired ACCEPTED", Invitation.Status.ACCEPTED),
    ("Another Expired PENDING", Invitation.Status.EXPIRED),
]

all_correct = True
for (label, inv), (_, expected_status) in zip(invitations, expected_results):
    inv.refresh_from_db()
    if inv.status == expected_status:
        print(f"✅ {label}: Correct status ({expected_status})")
    else:
        print(f"❌ {label}: Wrong status (got {inv.status}, expected {expected_status})")
        all_correct = False

print("\n6. Cleanup test data...")
# Clean up test data
Invitation.objects.filter(inviter=inviter).delete()
FamilyMember.objects.filter(user=inviter).delete()
family.delete()
inviter.delete()

print("\n" + "="*60)
if all_correct:
    print("✅ MANUAL TEST PASSED! All invitations processed correctly.")
else:
    print("❌ MANUAL TEST FAILED! Some invitations were not processed correctly.")
print("="*60)