from django.urls import path, include
from common.base.router import drf_router
# from .views import CountryListView
from .viewsets import ProductViewSet, CityViewSet

# write your urls here

urlpatterns = [
    # path('rest/v1/base/countries/', CountryListView.as_view(), name='country-list'),
    # path('rest/v1/base/countries/<str:lang>/', CountryListView.as_view(), name='country-list-lang'),
    path(r'rest/v1/cities/', include('cities_light.contrib.restframework3')),
]

drf_router.register(r'rest/v1/base/products', ProductViewSet, basename='base_product')
drf_router.register(r'rest/v1/cities/city', CityViewSet, basename='cities_city')

# urlpatterns += drf_router.urls
