from common.base.router import drf_router
from .viewsets import (UserProfileViewSet, OrganizationProfileViewSet, ProducerProfileViewSet, ImporterProfileViewSet,
                       PackhouseExporterProfileViewSet, TradeExporterProfileViewSet)

# write your urls here

drf_router.register(r'rest/v1/profiles/user-profile', UserProfileViewSet, basename='user-profile')
drf_router.register(r'rest/v1/profiles/organization-profile', OrganizationProfileViewSet, basename='organization-profile')
drf_router.register(r'rest/v1/profiles/producer-profile', ProducerProfileViewSet, basename='producer-profile')
drf_router.register(r'rest/v1/profiles/importer-profile', ImporterProfileViewSet, basename='importer-profile')
drf_router.register(r'rest/v1/profiles/packhouse-exporter-profile', PackhouseExporterProfileViewSet, basename='packhouse-exporter-profile')
drf_router.register(r'rest/v1/profiles/trade-exporter-profile', TradeExporterProfileViewSet, basename='trade-exporter-profile')

urlpatterns = drf_router.urls
