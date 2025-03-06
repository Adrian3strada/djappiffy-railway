from rest_framework import serializers
from .models import JobPosition
from django.utils.translation import gettext_lazy as _


class JobPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPosition
        fields = '__all__'