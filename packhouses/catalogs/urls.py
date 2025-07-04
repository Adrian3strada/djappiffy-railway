from common.base.router import drf_router
from .viewsets import (
    MarketViewSet, ProductMarketClassViewSet, VehicleViewSet, HarvestingCrewProviderViewSet,
    CrewChiefViewSet, ProductVarietyViewSet, ProductHarvestSizeKindViewSet, ProductPhenologyKindViewSet,
    ClientViewSet, ProviderViewSet, ProductViewSet, MaquiladoraViewSet, SupplyViewSet,
    ProductSizeViewSet, ProductPresentationViewSet, PackagingViewSet,  PalletViewSet,
    OrchardViewSet, HarvestingCrewViewSet, OrchardCertificationViewSet, OrchardGeoLocationViewSet, ProductRipenessViewSet,
    ServiceViewSet, PestProductKindViewSet, DiseaseProductKindViewSet, SizePackagingViewSet,
    OrchardForEudrViewSet, OrchardCertificationForEudrViewSet, OrchardGeoLocationForEudrViewSet
)

urlpatterns = []

drf_router.register(r'rest/v1/catalogs/market', MarketViewSet, basename='market')
drf_router.register(r'rest/v1/catalogs/product', ProductViewSet, basename='product')
drf_router.register(r'rest/v1/catalogs/pallet', PalletViewSet, basename='pallet')
drf_router.register(r'rest/v1/catalogs/product-market-class', ProductMarketClassViewSet, basename='market_class')
drf_router.register(r'rest/v1/catalogs/product-harvest-size-kind', ProductHarvestSizeKindViewSet,
                    basename='product_harvest_size_kind')
drf_router.register(r'rest/v1/catalogs/product-phenology', ProductPhenologyKindViewSet, basename='product_season_kind')
drf_router.register(r'rest/v1/catalogs/product-variety', ProductVarietyViewSet, basename='product_variety')
drf_router.register(r'rest/v1/catalogs/product-size', ProductSizeViewSet, basename='product_size')
drf_router.register(r'rest/v1/catalogs/product-presentation', ProductPresentationViewSet,
                    basename='product_presentation')
drf_router.register(r'rest/v1/catalogs/size-packaging', SizePackagingViewSet, basename='size_packaging')
# drf_router.register(r'rest/v1/catalogs/product-packaging-pallet', ProductPackagingPalletViewSet, basename='product_packaging_pallet')
drf_router.register(r'rest/v1/catalogs/product-packaging', PackagingViewSet, basename='product_packaging')
drf_router.register(r'rest/v1/catalogs/provider', ProviderViewSet, basename='provider')
drf_router.register(r'rest/v1/catalogs/supply', SupplyViewSet, basename='supply')
drf_router.register(r'rest/v1/catalogs/vehicle', VehicleViewSet, basename='vehicle')
drf_router.register(r'rest/v1/catalogs/harvesting-crew-provider', HarvestingCrewProviderViewSet,
                    basename='harvesting_crew_provider')
drf_router.register(r'rest/v1/catalogs/crew_chief', CrewChiefViewSet, basename='crew_chief')
drf_router.register(r'rest/v1/catalogs/client', ClientViewSet, basename='client')
drf_router.register(r'rest/v1/catalogs/orchard', OrchardViewSet, basename='orchard')
drf_router.register(r'rest/v1/catalogs/orchard-certification', OrchardCertificationViewSet,
                    basename='orchard_certification')
drf_router.register(r'rest/v1/catalogs/orchard-geolocation', OrchardGeoLocationViewSet, basename='orchard_geolocation')

drf_router.register(r'rest/v1/catalogs/harvesting-crew', HarvestingCrewViewSet, basename='harvesting_crew')
drf_router.register(r'rest/v1/catalogs/maquiladora', MaquiladoraViewSet, basename='maquiladora')
drf_router.register(r'rest/v1/catalogs/product-ripeness', ProductRipenessViewSet, basename='product_ripeness')
drf_router.register(r'rest/v1/catalogs/service', ServiceViewSet, basename='service')
drf_router.register(r'rest/v1/catalogs/pest-kinds', PestProductKindViewSet, basename='pest_kinds')
drf_router.register(r'rest/v1/catalogs/disease-kinds', DiseaseProductKindViewSet, basename='disease_kinds')

drf_router.register(r'rest/v1/catalogs/orchard-for-eudr', OrchardForEudrViewSet, basename='orchard_for_eudr')
drf_router.register(r'rest/v1/catalogs/orchard-certification-for-eudr', OrchardCertificationForEudrViewSet, basename='orchard_certification_for_eudr')
drf_router.register(r'rest/v1/catalogs/orchard-geolocation-for-eudr', OrchardGeoLocationForEudrViewSet, basename='orchard_geolocation_for_eudr')
urlpatterns += drf_router.urls
