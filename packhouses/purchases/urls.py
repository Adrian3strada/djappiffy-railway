from common.base.router import drf_router
from django.urls import path
from .viewsets import PaymentKindAdditionalInputViewSet, PurchaseOrderViewSet, ServiceOrderViewSet, FruitReceiptsViewSet
from .views import (requisition_pdf, CancelMassPaymentView)

urlpatterns = [
    path('dadmin/purchases/purchasemasspayment/cancel-mass-payment/<int:pk>/', CancelMassPaymentView.as_view(), name='set_masspayment_cancel'),
]


drf_router.register(r'rest/v1/purchases/payment-additional-inputs', PaymentKindAdditionalInputViewSet, basename='payment-additional-inputs')
drf_router.register(r'rest/v1/purchases/purchase-order', PurchaseOrderViewSet, basename='purchase-order')
drf_router.register(r'rest/v1/purchases/service-order', ServiceOrderViewSet, basename='service-order')
drf_router.register(r'rest/v1/purchases/fruit-receipts', FruitReceiptsViewSet, basename='get_fruit_receipts')


urlpatterns += drf_router.urls

