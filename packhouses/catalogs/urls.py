from common.base.router import drf_router
from django.urls import path
from . import views
from .models import ProductHarvestSizeKind
from .viewsets import (
    MarketStandardProductSizeViewSet, MarketViewSet, MarketClassViewSet, VehicleViewSet, HarvestingCrewProviderViewSet,
    CrewChiefViewSet, ProductVarietyViewSet, ProductHarvestSizeKindViewSet, ProductSeasonKindKindViewSet,
    ProductMassVolumeKindViewSet, ClientViewSet, ProviderViewSet, ProductViewSet, MaquiladoraViewSet, SupplyViewSet, MarketProductSizeViewSet,
    OrchardViewSet, HarvestingCrewViewSet
)

urlpatterns = []

drf_router.register(r'rest/v1/catalogs/market', MarketViewSet, basename='market')
drf_router.register(r'rest/v1/catalogs/market_class', MarketClassViewSet, basename='market_class')
drf_router.register(r'rest/v1/catalogs/market_standard_product_size', MarketStandardProductSizeViewSet, basename='market_standard_product_size')
drf_router.register(r'rest/v1/catalogs/product', ProductViewSet, basename='product')
drf_router.register(r'rest/v1/catalogs/product_harvest_size_kind', ProductHarvestSizeKindViewSet, basename='product_harvest_size_kind')
drf_router.register(r'rest/v1/catalogs/product_season_kind', ProductSeasonKindKindViewSet, basename='product_season_kind')
drf_router.register(r'rest/v1/catalogs/product_mass_volume_kind', ProductMassVolumeKindViewSet, basename='product_mass_volume_kind')
drf_router.register(r'rest/v1/catalogs/product_variety', ProductVarietyViewSet, basename='product_variety')
drf_router.register(r'rest/v1/catalogs/product_size', MarketProductSizeViewSet, basename='product_size')
drf_router.register(r'rest/v1/catalogs/provider', ProviderViewSet, basename='provider')
drf_router.register(r'rest/v1/catalogs/supply', SupplyViewSet, basename='supply')
drf_router.register(r'rest/v1/catalogs/vehicle', VehicleViewSet, basename='vehicle')
drf_router.register(r'rest/v1/catalogs/harvesting_crew_provider', HarvestingCrewProviderViewSet, basename='harvesting_crew_provider')
drf_router.register(r'rest/v1/catalogs/crew_chief', CrewChiefViewSet, basename='crew_chief')
drf_router.register(r'rest/v1/catalogs/client', ClientViewSet, basename='client')
drf_router.register(r'rest/v1/catalogs/orchard', OrchardViewSet, basename='orchard')
drf_router.register(r'rest/v1/catalogs/harvesting_crew', HarvestingCrewViewSet, basename='harvesting_crew')
drf_router.register(r'rest/v1/catalogs/maquiladora', MaquiladoraViewSet, basename='maquiladora')


urlpatterns += drf_router.urls
