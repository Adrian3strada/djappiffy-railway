from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from packhouses.packhouse_settings.models import PaymentKindAdditionalInput
from .models import PurchaseOrder, ServiceOrder, FruitPurchaseOrderReceipt

class PaymentKindAdditionalInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentKindAdditionalInput
        fields = '__all__'

class PurchaseOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = '__all__'

class ServiceOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceOrder
        fields = '__all__'

class FruitReceiptsSerializer(serializers.ModelSerializer):
    provider_name = serializers.SerializerMethodField()

    class Meta:
        model = FruitPurchaseOrderReceipt
        fields = [
            'id', 'ooid', 'receipt_kind', 'quantity', 'unit_price', 'total_cost',
            'balance_payable', 'status', 'created_at', 'cancellation_date',
            'fruit_purchase_order', 'provider', 'provider_name',
            'price_category', 'created_by', 'canceled_by',
        ]

    def get_provider_name(self, obj):
        return obj.provider.name if obj.provider else None

