from common.base.router import drf_router
from django.urls import path
from . import views
from .viewsets import MarketStandardProductSizeViewSet

urlpatterns = [
    path(r'market_standard_product_size/<int:market_id>/', views.get_market_standard_product_size, name='get_market_standard_product_size'),
]

drf_router.register(r'rest/v1/catalogs/market_standard_product_size', MarketStandardProductSizeViewSet, basename='market_standard_product_size')

urlpatterns += drf_router.urls
