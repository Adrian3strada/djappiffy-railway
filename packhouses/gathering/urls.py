from common.base.router import drf_router
from django.urls import path
from .viewsets import ScheduleHarvestVehicleViewSet

urlpatterns = []

drf_router.register(r'rest/v1/gathering/harvest-cutting-vehicle', ScheduleHarvestVehicleViewSet, basename='harvest-cutting-vehicle')

urlpatterns += drf_router.urls
