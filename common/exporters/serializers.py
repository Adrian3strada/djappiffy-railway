from rest_framework import serializers
from .models import ExportRequest, ExportRequestProducer, ExportRequestPayment


class ExportRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExportRequest
        fields = '__all__'


class ExportRequestProducerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExportRequestProducer
        fields = '__all__'


class ExportRequestPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExportRequestPayment
        fields = '__all__'
