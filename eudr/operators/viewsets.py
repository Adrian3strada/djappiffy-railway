from rest_framework import viewsets
from .models import OperatorParcel, ProductionInterval, LegalCompliance
from .serializers import OperatorParcelSerializer, ProductionIntervalSerializer, LegalComplianceSerializer


class OperatorParcelViewSet(viewsets.ModelViewSet):
    serializer_class = OperatorParcelSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return OperatorParcel.objects.all()
        else:
            return OperatorParcel.objects.filter(eudr_operator__organization__organization_users__user=self.request.user)


class ProductionIntervalViewSet(viewsets.ModelViewSet):
    serializer_class = ProductionIntervalSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return ProductionInterval.objects.all()
        else:
            return ProductionInterval.objects.filter(operator_parcel__eudr_operator__organization__organization_users__user=self.request.user)
      
        
class LegalComplianceViewSet(viewsets.ModelViewSet):
    serializer_class = LegalComplianceSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return LegalCompliance.objects.all()
        else:
            return LegalCompliance.objects.filter(operator_parcel__eudr_operator__organization__organization_users__user=self.request.user)