from rest_framework import serializers
from packhouses.gathering.models import ScheduleHarvestVehicle
from django.utils.translation import gettext_lazy as _

class ScheduleHarvestVehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleHarvestVehicle
        fields = '__all__'
