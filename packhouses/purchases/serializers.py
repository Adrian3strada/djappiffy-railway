from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from packhouses.packhouse_settings.models import PaymentKindAdditionalInput
from .models import PurchaseOrder, ServiceOrder

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

