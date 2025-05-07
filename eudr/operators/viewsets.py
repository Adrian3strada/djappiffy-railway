from rest_framework import viewsets
from .models import OperatorParcel
from .serializers import ParcelSerializer


class OperatorParcelViewSet(viewsets.ModelViewSet):
    serializer_class = ParcelSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return OperatorParcel.objects.all()
        else:

            return OperatorParcel.objects.filter(eudr_operator__organization__organization_users__user=self.request.user)

