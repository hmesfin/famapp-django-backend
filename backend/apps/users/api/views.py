from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.users.models import User

from .serializers import UserSerializer


class UserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "public_id"

    def get_queryset(self, *args, **kwargs):
        return self.queryset.filter(public_id=self.request.user.public_id)

    @action(detail=False)
    def me(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    @action(detail=False, methods=["get"])
    def search(self, request):
        """Search for users by email or name"""
        query = request.query_params.get("q", "").strip()

        if len(query) < 2:
            return Response([])

        # Search by email, first name, or last name
        users = User.objects.filter(
            Q(email__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query),
        ).exclude(
            public_id=request.user.public_id,  # Exclude current user
        )[:10]  # Limit to 10 results

        serializer = UserSerializer(users, many=True, context={"request": request})
        return Response(serializer.data)
