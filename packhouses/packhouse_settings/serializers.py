from rest_framework import serializers
from .models import OrchardCertificationKind


class OrchardCertificationKindSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrchardCertificationKind
        fields = '__all__'

