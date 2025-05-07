from django.urls import path, include
from common.base.router import drf_router
from .viewsets import ParcelViewSet

# write your urls here

urlpatterns = []

drf_router.register(r'rest/v1/eudr/operator/parcel', ParcelViewSet, basename='base_operator_parcel')

urlpatterns += drf_router.urls
