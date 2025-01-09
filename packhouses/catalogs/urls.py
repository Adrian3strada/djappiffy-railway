from common.base.router import drf_router
from django.urls import path
from . import views
from .models import ProductHarvestSizeKind
from .viewsets import (
    MarketStandardProductSizeViewSet, MarketViewSet, VehicleViewSet, HarvestingCrewProviderViewSet,
    CrewChiefViewSet, ProductVarietyViewSet, ProductHarvestSizeKindViewSet, ProductQualityKindKindViewSet,
    ProductMassVolumeKindViewSet, ClientViewSet, ProviderViewSet, ProductViewSet, SupplyViewSet
)

urlpatterns = []

drf_router.register(r'rest/v1/catalogs/market', MarketViewSet, basename='market')
drf_router.register(r'rest/v1/catalogs/market_standard_product_size', MarketStandardProductSizeViewSet, basename='market_standard_product_size')
drf_router.register(r'rest/v1/catalogs/product', ProductViewSet, basename='product')
drf_router.register(r'rest/v1/catalogs/product_harvest_size_kind', ProductHarvestSizeKindViewSet, basename='product_harvest_size_kind')
drf_router.register(r'rest/v1/catalogs/product_quality_kind', ProductQualityKindKindViewSet, basename='product_quality_kind')
drf_router.register(r'rest/v1/catalogs/product_mass_volume_kind', ProductMassVolumeKindViewSet, basename='product_mass_volume_kind')
drf_router.register(r'rest/v1/catalogs/product_variety', ProductVarietyViewSet, basename='product_variety')
drf_router.register(r'rest/v1/catalogs/provider', ProviderViewSet, basename='provider')
drf_router.register(r'rest/v1/catalogs/supply', SupplyViewSet, basename='supply')
drf_router.register(r'rest/v1/catalogs/vehicle', VehicleViewSet, basename='vehicle')
drf_router.register(r'rest/v1/catalogs/harvesting_crew_provider', HarvestingCrewProviderViewSet, basename='harvesting_crew_provider')
drf_router.register(r'rest/v1/catalogs/crew_chief', CrewChiefViewSet, basename='crew_chief')
drf_router.register(r'rest/v1/catalogs/client', ClientViewSet, basename='client')


urlpatterns += drf_router.urls
