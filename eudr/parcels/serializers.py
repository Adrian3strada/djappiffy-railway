from rest_framework import serializers
from .models import Parcel
from rest_framework_gis.serializers import GeoFeatureModelSerializer

#


class ParcelSerializer(GeoFeatureModelSerializer):
    producer_name = serializers.SerializerMethodField()

    def get_producer_name(self, obj):
        return obj.producer.name

    class Meta:
        model = Parcel
        fields = "__all__"
        geo_field = "geom"
        read_only_fields = ['producer_name']
