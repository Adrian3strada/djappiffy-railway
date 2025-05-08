from rest_framework import serializers
from .models import OperatorParcel, ProductionInterval, LegalCompliance
from rest_framework_gis.serializers import GeoFeatureModelSerializer

#

class OperatorParcelSerializer(GeoFeatureModelSerializer):
    eudr_operator_name = serializers.SerializerMethodField()

    def get_eudr_operator_name(self, obj):
        return obj.eudr_operator.name

    class Meta:
        model = OperatorParcel
        fields = "__all__"
        geo_field = "geom"
        read_only_fields = ['eudr_operator_name']


class ProductionIntervalSerializer(serializers.ModelSerializer):
    operator_parcel_name = serializers.CharField(source='operator_parcel.name', read_only=True)

    class Meta:
        model = ProductionInterval
        fields = ['operator_parcel', 'operator_parcel_name', 'start_date', 'end_date']
        read_only_fields = ['operator_parcel_name']

    

class LegalComplianceSerializer(serializers.ModelSerializer):
    operator_parcel_name = serializers.CharField(source='operator_parcel.name', read_only=True)

    class Meta:
        model = LegalCompliance
        fields = [
            'operator_parcel', 'operator_parcel_name',
            'land_use_right', 'third_party_rights', 'labor_and_human_rights',
            'free_prior_informed_consent', 'environmental_protection'
        ]
        read_only_fields = ['operator_parcel_name']
