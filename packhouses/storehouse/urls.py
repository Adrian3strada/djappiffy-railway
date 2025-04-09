from common.base.router import drf_router
from .viewsets import PurchaseOrderSupplyViewSet


urlpatterns = []

drf_router.register(r'rest/v1/storehouse/purchases-order-supplies', PurchaseOrderSupplyViewSet, basename='purchases-order-supplies')

urlpatterns += drf_router.urls
