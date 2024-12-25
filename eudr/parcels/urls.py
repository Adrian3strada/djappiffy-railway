from django.urls import path, include
from common.base.router import drf_router
from .viewsets import ParcelViewSet

# write your urls here

urlpatterns = []

drf_router.register(r'rest/v1/eudr/parcel', ParcelViewSet, basename='base_parcel')

urlpatterns += drf_router.urls
