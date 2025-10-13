"""
Custom DRF mixins for FamApp authorization.

Following Django REST Framework patterns:
- FamilyAccessMixin: Automatically filters queryset by family membership

Ham Dog & TC building reusable authorization patterns! 🔒
"""


class FamilyAccessMixin:
    """
    Mixin for ViewSets handling family-scoped resources.

    Automatically filters queryset to only include resources from families
    where the request user is a member.

    Usage:
        class TodoViewSet(FamilyAccessMixin, viewsets.ModelViewSet):
            queryset = Todo.objects.all()
            ...

    Filtering Logic:
        - Includes resources where family__members contains request.user
        - Excludes resources from soft-deleted families (family.is_deleted=True)
        - Excludes soft-deleted resources (resource.is_deleted=True)
        - Preserves any additional filters on the base queryset

    Assumptions:
        - Resource model has a 'family' ForeignKey to Family
        - Resource model inherits from BaseModel (has is_deleted field)
        - Family model has 'members' ManyToManyField to User
    """

    def get_queryset(self):
        """
        Filter queryset to resources in families where user is a member.

        Returns:
            QuerySet: Filtered queryset excluding soft-deleted families and resources
        """
        # Get base queryset (may have additional filters)
        queryset = super().get_queryset()

        # Get current user from request
        user = self.request.user

        # Filter by family membership and exclude soft-deleted families/resources
        return queryset.filter(
            family__members=user,  # User is member of the family
            family__is_deleted=False,  # Family not soft-deleted
            is_deleted=False,  # Resource itself not soft-deleted
        )
