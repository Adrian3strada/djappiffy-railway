from common.base.router import drf_router
from django.urls import path
from .viewsets import PaymentKindAdditionalInputViewSet

urlpatterns = []

drf_router.register(r'rest/v1/purchases/payment-additional-inputs', PaymentKindAdditionalInputViewSet, basename='payment-additional-inputs')

urlpatterns += drf_router.urls
