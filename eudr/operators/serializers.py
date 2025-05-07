from rest_framework import serializers
from .models import OperatorParcel
from rest_framework_gis.serializers import GeoFeatureModelSerializer

#


class ParcelSerializer(GeoFeatureModelSerializer):
    eudr_operator_name = serializers.SerializerMethodField()

    def get_eudr_operator_name(self, obj):
        return obj.eudr_operator.name

    class Meta:
        model = OperatorParcel
        fields = "__all__"
        geo_field = "geom"
        read_only_fields = ['eudr_operator_name']
