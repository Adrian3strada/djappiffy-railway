from rest_framework import viewsets
from rest_framework.exceptions import NotAuthenticated
from .serializers import ScheduleHarvestVehicleSerializer
from packhouses.gathering.models import ScheduleHarvestVehicle


class ScheduleHarvestVehicleViewSet(viewsets.ModelViewSet):
    serializer_class = ScheduleHarvestVehicleSerializer
    filterset_fields = ['id', 'vehicle_id']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        return ScheduleHarvestVehicle.objects.filter(organization=self.request.organization)


