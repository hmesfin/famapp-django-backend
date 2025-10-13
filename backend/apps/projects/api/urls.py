"""
API URL Configuration for Projects
Ham Dog & TC's RESTful routing
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.projects.api.views import (
    ProjectViewSet, SprintViewSet, TaskViewSet, CommentViewSet
)

app_name = 'projects'

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'sprints', SprintViewSet, basename='sprint')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
]