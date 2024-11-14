
from rest_framework import mixins, viewsets, permissions
from .models import (UserProfile, OrganizationProfile, ProducerProfile, ImporterProfile, PackhouseExporterProfile,
                     TradeExporterProfile)
from .serializers import (UserProfileSerializer, OrganizationProfileSerializer, ProducerProfileSerializer,
                          ImporterProfileSerializer, PackhouseExporterProfileSerializer, TradeExporterProfileSerializer)

#


class UserProfileViewSet(viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated]
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class OrganizationProfileViewSet(viewsets.ModelViewSet):
    queryset = OrganizationProfile.objects.all()
    serializer_class = OrganizationProfileSerializer

    # TODO: Implementar la lógica para que solo los propietarios de la organización puedan ver y modificar los perfiles de la organización

    def perform_create(self, serializer):
        serializer.save()


class ProducerProfileViewSet(viewsets.ModelViewSet):
    queryset = ProducerProfile.objects.all()
    serializer_class = ProducerProfileSerializer

    # TODO: Implementar la lógica para que solo los propietarios de la organización puedan ver y modificar los perfiles de la organización

    def perform_create(self, serializer):
        serializer.save()


class ImporterProfileViewSet(viewsets.ModelViewSet):
    queryset = ImporterProfile.objects.all()
    serializer_class = ImporterProfileSerializer

    # TODO: Implementar la lógica para que solo los propietarios de la organización puedan ver y modificar los perfiles de la organización

    def perform_create(self, serializer):
        serializer.save()


class PackhouseExporterProfileViewSet(viewsets.ModelViewSet):
    queryset = PackhouseExporterProfile.objects.all()
    serializer_class = PackhouseExporterProfileSerializer

    # TODO: Implementar la lógica para que solo los propietarios de la organización puedan ver y modificar los perfiles de la organización

    def perform_create(self, serializer):
        serializer.save()


class TradeExporterProfileViewSet(viewsets.ModelViewSet):
    queryset = TradeExporterProfile.objects.all()
    serializer_class = TradeExporterProfileSerializer

    # TODO: Implementar la lógica para que solo los propietarios de la organización puedan ver y modificar los perfiles de la organización

    def perform_create(self, serializer):
        serializer.save()
