from rest_framework import viewsets
from rest_framework.exceptions import NotAuthenticated
from rest_framework.permissions import IsAuthenticated
from .serializers import ScheduleHarvestVehicleSerializer
from packhouses.gathering.models import ScheduleHarvestVehicle


class ScheduleHarvestVehicleViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ScheduleHarvestVehicleSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['harvest_cutting_id', 'vehicle_id']

    def get_queryset(self):
        return ScheduleHarvestVehicle.objects.filter(
            harvest_cutting_id=self.request.query_params.get('harvest_cutting_id'),
            vehicle_id=self.request.query_params.get('vehicle_id')
        ).select_related('vehicle', 'harvest_cutting')
