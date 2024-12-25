from rest_framework import serializers
from .models import OrchardCertificationKind, OrchardCertificationVerifier


class OrchardCertificationKindSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrchardCertificationKind
        fields = '__all__'


class OrchardCertificationVerifierSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrchardCertificationVerifier
        fields = '__all__'
