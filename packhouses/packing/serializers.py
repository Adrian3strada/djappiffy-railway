from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import PackingPallet

# Create a serializer for Packing


class PackingPalletSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PackingPallet
        fields = '__all__'

    def get_name(self, obj):
        return str(obj)
