from django.urls import path, include
from common.base.router import drf_router
from .viewsets import (ProductKindViewSet, CityViewSet, SubRegionViewSet, RegionViewSet, CountryViewSet,
                       CapitalFrameworkViewSet, CountryProductStandardPackagingViewSet,
                       CountryProductStandardSizeViewSet)

# write your urls here

urlpatterns = [
    # path('rest/v1/base/countries/', CountryListView.as_view(), name='country-list'),
    # path('rest/v1/base/countries/<str:lang>/', CountryListView.as_view(), name='country-list-lang'),
    path(r'rest/v1/cities/', include('cities_light.contrib.restframework3')),
]

drf_router.register(r'rest/v1/base/product-kind', ProductKindViewSet, basename='base_productkind')
drf_router.register(r'rest/v1/base/capital-framework', CapitalFrameworkViewSet, basename='capital_framework')
drf_router.register(r'rest/v1/base/country-product-standard-size', CountryProductStandardSizeViewSet, basename='market_product_size_standard_size')
drf_router.register(r'rest/v1/base/country-product-standard-packaging', CountryProductStandardPackagingViewSet, basename='market_product_size_standard_packaging')
drf_router.register(r'rest/v1/cities/country', CountryViewSet, basename='cities_country')
drf_router.register(r'rest/v1/cities/region', RegionViewSet, basename='cities_region')
drf_router.register(r'rest/v1/cities/subregion', SubRegionViewSet, basename='cities_subregion')
drf_router.register(r'rest/v1/cities/city', CityViewSet, basename='cities_city')

# urlpatterns += drf_router.urls
# productpackagingstandard
