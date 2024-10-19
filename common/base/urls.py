from django.urls import path
from common.base.router import drf_router
# from .views import CountryListView
from .viewsets import ProductViewSet

# write your urls here

urlpatterns = [
    # path('rest/v1/base/countries/', CountryListView.as_view(), name='country-list'),
    # path('rest/v1/base/countries/<str:lang>/', CountryListView.as_view(), name='country-list-lang'),
]

drf_router.register(r'rest/v1/base/products', ProductViewSet, basename='product')

# urlpatterns += drf_router.urls
