"""
Custom DRF permissions for FamApp.

Following Django REST Framework permission patterns:
- IsFamilyMember: Ensures user is a member of the family
- IsFamilyAdmin: Ensures user is an organizer (admin) of the family

Ham Dog & TC building bulletproof authorization! 🔒
"""

from rest_framework import permissions

from apps.shared.models import Family, FamilyMember


class IsFamilyMember(permissions.BasePermission):
  """
  Permission to check if user is a member of the family.

  This permission checks both at the view level (has_permission) and
  object level (has_object_permission).

  View-level: Looks for 'family_public_id' in view kwargs
  Object-level: Checks if the object is a Family and user is a member
  """

  message = "You must be a family member to access this resource."

  def has_permission(self, request, view):
    """
    Check if user is authenticated and is a member of the family.

    Looks for 'family_public_id' in view.kwargs to identify the family.
    """
    # User must be authenticated
    if not request.user or not request.user.is_authenticated:
      return False

    # Get family_public_id from view kwargs
    family_public_id = view.kwargs.get("family_public_id")
    if not family_public_id:
      # No family specified in URL, allow the check to proceed
      # (object-level permission will handle it)
      return True

    # Check if family exists and user is a member
    try:
      family = Family.objects.get(public_id=family_public_id)
      return FamilyMember.objects.filter(
        family=family, user=request.user
      ).exists()
    except Family.DoesNotExist:
      return False

  def has_object_permission(self, request, view, obj):
    """
    Check if user is a member of the family object.

    Works when obj is a Family or any model with a 'family' relationship.
    """
    # User must be authenticated
    if not request.user or not request.user.is_authenticated:
      return False

    # If obj is a Family, check direct membership
    if isinstance(obj, Family):
      return FamilyMember.objects.filter(
        family=obj, user=request.user
      ).exists()

    # If obj has a 'family' attribute, check membership in that family
    if hasattr(obj, "family"):
      return FamilyMember.objects.filter(
        family=obj.family, user=request.user
      ).exists()

    # Default to deny if we can't determine the family
    return False


class IsFamilyAdmin(permissions.BasePermission):
  """
  Permission to check if user is an organizer (admin) of the family.

  Only organizers can perform administrative actions like:
  - Updating family settings
  - Inviting/removing members
  - Changing member roles
  - Deleting the family

  Inherits from IsFamilyMember logic and adds role check.
  """

  message = "You must be a family organizer to perform this action."

  def has_permission(self, request, view):
    """
    Check if user is authenticated and is an organizer of the family.

    Looks for 'family_public_id' in view.kwargs to identify the family.
    """
    # User must be authenticated
    if not request.user or not request.user.is_authenticated:
      return False

    # Get family_public_id from view kwargs
    family_public_id = view.kwargs.get("family_public_id")
    if not family_public_id:
      # No family specified in URL, allow the check to proceed
      # (object-level permission will handle it)
      return True

    # Check if family exists and user is an organizer
    try:
      family = Family.objects.get(public_id=family_public_id)
      return FamilyMember.objects.filter(
        family=family, user=request.user, role=FamilyMember.Role.ORGANIZER
      ).exists()
    except Family.DoesNotExist:
      return False

  def has_object_permission(self, request, view, obj):
    """
    Check if user is an organizer of the family object.

    Works when obj is a Family or any model with a 'family' relationship.
    """
    # User must be authenticated
    if not request.user or not request.user.is_authenticated:
      return False

    # If obj is a Family, check organizer role
    if isinstance(obj, Family):
      return FamilyMember.objects.filter(
        family=obj, user=request.user, role=FamilyMember.Role.ORGANIZER
      ).exists()

    # If obj has a 'family' attribute, check organizer role in that family
    if hasattr(obj, "family"):
      return FamilyMember.objects.filter(
        family=obj.family, user=request.user, role=FamilyMember.Role.ORGANIZER
      ).exists()

    # Default to deny if we can't determine the family
    return False
