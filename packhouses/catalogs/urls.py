from common.base.router import drf_router
from django.urls import path
from . import views
from .viewsets import MarketStandardProductSizeViewSet, MarketViewSet

urlpatterns = []

drf_router.register(r'rest/v1/catalogs/market_standard_product_size', MarketStandardProductSizeViewSet, basename='market_standard_product_size')
drf_router.register(r'rest/v1/catalogs/market', MarketViewSet, basename='market')

urlpatterns += drf_router.urls
