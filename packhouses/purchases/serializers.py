from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from packhouses.packhouse_settings.models import PaymentKindAdditionalInput

class PaymentKindAdditionalInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentKindAdditionalInput
        fields = '__all__'
