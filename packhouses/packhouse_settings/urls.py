from common.base.router import drf_router
from django.urls import path
from . import views
from .viewsets import OrchardCertificationKindViewSet

urlpatterns = []

drf_router.register(r'rest/v1/packhouse-settings/orchard-certification-kind', OrchardCertificationKindViewSet, basename='packhouse-settings_orchard-certification-kind')

urlpatterns += drf_router.urls
