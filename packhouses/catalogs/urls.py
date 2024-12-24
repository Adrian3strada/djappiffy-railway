from common.base.router import drf_router
from django.urls import path
from . import views
from .viewsets import (
                MarketStandardProductSizeViewSet, MarketViewSet, VehicleViewSet, HarvestingCrewProviderViewSet,
                CrewChiefViewSet
                )

urlpatterns = []

drf_router.register(r'rest/v1/catalogs/market_standard_product_size', MarketStandardProductSizeViewSet, basename='market_standard_product_size')
drf_router.register(r'rest/v1/catalogs/market', MarketViewSet, basename='market')
drf_router.register(r'rest/v1/catalogs/vehicle', VehicleViewSet, basename='vehicle')
drf_router.register(r'rest/v1/catalogs/harvesting_crew_provider', HarvestingCrewProviderViewSet, basename='harvesting_crew_provider')
drf_router.register(r'rest/v1/catalogs/crew_chief', CrewChiefViewSet, basename='crew_chief')


urlpatterns += drf_router.urls
