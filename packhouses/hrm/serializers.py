from rest_framework import serializers
from .models import WorkShiftSchedule, JobPosition
from django.utils.translation import gettext_lazy as _


class WorkShiftScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkShiftSchedule
        fields = '__all__'

class JobPositionSerializer(serializers.ModelSerializer):
    work_shift_schedules = WorkShiftScheduleSerializer(many=True, read_only=True)

    class Meta:
        model = JobPosition
        fields = '__all__'