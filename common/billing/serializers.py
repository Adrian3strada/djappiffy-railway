from rest_framework import serializers
from .models import LegalEntityCategory


# Serializers define the API representation.


class LegalEntityCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalEntityCategory
        fields = "__all__"
