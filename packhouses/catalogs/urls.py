from common.base.router import drf_router
from django.urls import path
from . import views
from .models import ProductHarvestSizeKind
from .viewsets import (
    MarketViewSet, ProductMarketClassViewSet, VehicleViewSet, HarvestingCrewProviderViewSet,
    CrewChiefViewSet, ProductVarietyViewSet, ProductHarvestSizeKindViewSet, ProductPhenologyKindViewSet,
    ClientViewSet, ProviderViewSet, ProductViewSet, MaquiladoraViewSet, SupplyViewSet,
    ProductSizeViewSet, ProductPresentationViewSet, ProductPackagingViewSet, ProductPackagingPalletViewSet, PalletViewSet,
    OrchardViewSet, HarvestingCrewViewSet, OrchardCertificationViewSet, PackagingViewSet, ProductRipenessViewSet,
    ServiceViewSet
)



urlpatterns = []

drf_router.register(r'rest/v1/catalogs/market', MarketViewSet, basename='market')
drf_router.register(r'rest/v1/catalogs/product', ProductViewSet, basename='product')
drf_router.register(r'rest/v1/catalogs/pallet', PalletViewSet, basename='pallet')
drf_router.register(r'rest/v1/catalogs/product-market-class', ProductMarketClassViewSet, basename='market_class')
drf_router.register(r'rest/v1/catalogs/product-harvest-size-kind', ProductHarvestSizeKindViewSet, basename='product_harvest_size_kind')
drf_router.register(r'rest/v1/catalogs/product-phenology', ProductPhenologyKindViewSet, basename='product_season_kind')
drf_router.register(r'rest/v1/catalogs/product-variety', ProductVarietyViewSet, basename='product_variety')
drf_router.register(r'rest/v1/catalogs/product-size', ProductSizeViewSet, basename='product_size')
drf_router.register(r'rest/v1/catalogs/product-presentation', ProductPresentationViewSet, basename='product_presentation')
drf_router.register(r'rest/v1/catalogs/product-packaging', ProductPackagingViewSet, basename='product_packaging')
drf_router.register(r'rest/v1/catalogs/product-packaging-pallet', ProductPackagingPalletViewSet, basename='product_packaging_pallet')
drf_router.register(r'rest/v1/catalogs/packaging', PackagingViewSet, basename='packaging')
drf_router.register(r'rest/v1/catalogs/provider', ProviderViewSet, basename='provider')
drf_router.register(r'rest/v1/catalogs/supply', SupplyViewSet, basename='supply')
drf_router.register(r'rest/v1/catalogs/vehicle', VehicleViewSet, basename='vehicle')
drf_router.register(r'rest/v1/catalogs/harvesting-crew-provider', HarvestingCrewProviderViewSet, basename='harvesting_crew_provider')
drf_router.register(r'rest/v1/catalogs/crew_chief', CrewChiefViewSet, basename='crew_chief')
drf_router.register(r'rest/v1/catalogs/client', ClientViewSet, basename='client')
drf_router.register(r'rest/v1/catalogs/orchard', OrchardViewSet, basename='orchard')
drf_router.register(r'rest/v1/catalogs/harvesting-crew', HarvestingCrewViewSet, basename='harvesting_crew')
drf_router.register(r'rest/v1/catalogs/maquiladora', MaquiladoraViewSet, basename='maquiladora')
drf_router.register(r'rest/v1/catalogs/orchard-certification', OrchardCertificationViewSet, basename='orchard_certification')
drf_router.register(r'rest/v1/catalogs/product-ripeness', ProductRipenessViewSet, basename='product_ripeness')
drf_router.register(r'rest/v1/catalogs/service', ServiceViewSet, basename='service')

urlpatterns += drf_router.urls
