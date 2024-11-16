from rest_framework import serializers
from .models import Parcel

#


class ParcelSerializer(serializers.ModelSerializer):
    producer_name = serializers.SerializerMethodField()

    def get_producer_name(self, obj):
        return obj.producer.name

    class Meta:
        model = Parcel
        fields = "__all__"
        read_only_fields = ['producer_name']
