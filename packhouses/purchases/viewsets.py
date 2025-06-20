from rest_framework import viewsets
from rest_framework.exceptions import NotAuthenticated, ParseError
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import (PaymentKindAdditionalInputSerializer, PurchaseOrderSerializer, ServiceOrderSerializer,
                          FruitReceiptsSerializer)
from packhouses.packhouse_settings.models import PaymentKindAdditionalInput
from packhouses.packhouse_settings.models import PaymentKind
from rest_framework.response import Response
from .models import PurchaseOrder, ServiceOrder, FruitPurchaseOrderReceipt



class PaymentKindAdditionalInputViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentKindAdditionalInputSerializer
    queryset = PaymentKindAdditionalInput.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['payment_kind', 'is_enabled',]
    pagination_class = None

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            raise NotAuthenticated()
        return super().get_queryset()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        requires_bank = False
        payment_kind_id = request.query_params.get('payment_kind')
        if payment_kind_id:
            try:
                pk = PaymentKind.objects.get(id=payment_kind_id)
                requires_bank = pk.requires_bank
            except PaymentKind.DoesNotExist:
                pass

        return Response({
            'requires_bank': requires_bank,
            'additional_inputs': serializer.data
        })

class PurchaseOrderViewSet(viewsets.ModelViewSet):
    serializer_class = PurchaseOrderSerializer
    filterset_fields = ['id', 'ooid', 'provider', 'currency', 'status']
    filter_backends = [DjangoFilterBackend]
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        qs = PurchaseOrder.objects.filter(
            organization=self.request.organization,
            balance_payable__gt=0
        ).order_by('id')

        provider = self.request.query_params.get('provider')
        currency = self.request.query_params.get('currency')

        filters = {'status': 'closed'}
        if provider:
            filters['provider_id'] = provider
        if currency:
            filters['currency_id'] = currency

        return qs.filter(**filters)


class ServiceOrderViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceOrderSerializer
    filterset_fields = ['id', 'provider', 'currency']
    filter_backends = [DjangoFilterBackend]
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        qs = ServiceOrder.objects.filter(
            organization=self.request.organization,
            balance_payable__gt=0
        ).order_by('id')

        provider = self.request.query_params.get('provider')
        currency = self.request.query_params.get('currency')

        if provider:
            qs = qs.filter(provider_id=provider)
        if currency:
            qs = qs.filter(currency_id=currency)

        return qs


class FruitReceiptsViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar recibos de fruta.
    Permite filtrar por ID del recibo o por ID de la orden de compra.
    """
    serializer_class = FruitReceiptsSerializer
    filterset_fields = ['id', 'fruit_purchase_order']
    filter_backends = [DjangoFilterBackend]
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            raise NotAuthenticated("Debes iniciar sesión para ver esta información.")

        org = self.request.organization

        receipt_id = self.kwargs.get('pk') or self.request.query_params.get('id')
        order_id = self.request.query_params.get('fruit_purchase_order')

        queryset = FruitPurchaseOrderReceipt.objects.filter(
            fruit_purchase_order__organization=org
        )

        if receipt_id:
            try:
                receipt_id = int(receipt_id)
                queryset = queryset.filter(id=receipt_id)
            except (ValueError, TypeError):
                raise ParseError("'id' debe ser un número válido.")

        if order_id:
            try:
                order_id = int(order_id)
                queryset = queryset.filter(fruit_purchase_order_id=order_id)
            except (ValueError, TypeError):
                raise ParseError("'fruit_purchase_order' debe ser un número válido.")

        return queryset
