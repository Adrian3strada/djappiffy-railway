from django.urls import path
from common.base.router import drf_router
from .viewsets import JobPositionViewSet

urlpatterns = []

drf_router.register(r'rest/v1/hrm/job-position', JobPositionViewSet, basename='job_position')

urlpatterns += drf_router.urls
