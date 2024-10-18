from rest_framework import viewsets
from .models import ExportRequest, ExportRequestProducer, ExportRequestPayment
from .serializers import ExportRequestSerializer, ExportRequestProducerSerializer, ExportRequestPaymentSerializer


class ExportRequestViewSet(viewsets.ModelViewSet):
    queryset = ExportRequest.objects.all()
    serializer_class = ExportRequestSerializer


class ExportRequestProducerViewSet(viewsets.ModelViewSet):
    queryset = ExportRequestProducer.objects.all()
    serializer_class = ExportRequestProducerSerializer


class ExportRequestPaymentViewSet(viewsets.ModelViewSet):
    queryset = ExportRequestPayment.objects.all()
    serializer_class = ExportRequestPaymentSerializer
