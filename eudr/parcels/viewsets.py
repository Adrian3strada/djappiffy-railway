from rest_framework import viewsets
from .models import Parcel
from .serializers import ParcelSerializer

#


class ParcelViewSet(viewsets.ModelViewSet):
    queryset = Parcel.objects.all()
    serializer_class = ParcelSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Parcel.objects.all()
        else:

            return Parcel.objects.filter(producer__organization__organization_users__user=self.request.user)

