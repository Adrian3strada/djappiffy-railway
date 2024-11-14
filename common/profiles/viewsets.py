from rest_framework import viewsets, permissions
from .models import (UserProfile, OrganizationProfile, ProducerProfile, ImporterProfile, PackhouseExporterProfile,
                     TradeExporterProfile)
from .serializers import (UserProfileSerializer, OrganizationProfileSerializer, ProducerProfileSerializer,
                          ImporterProfileSerializer, PackhouseExporterProfileSerializer, TradeExporterProfileSerializer)
from .permissions import IsOrganizationMember


class BaseOrganizationProfileViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOrganizationMember]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return self.queryset
        return self.queryset.filter(organization__organizationuser__user=user)

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        if not self.request.user.is_superuser:
            serializer.validated_data.pop('organization', None)
        serializer.save()


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return self.queryset
        return self.queryset.filter(user=user)


class OrganizationProfileViewSet(BaseOrganizationProfileViewSet):
    queryset = OrganizationProfile.objects.all()
    serializer_class = OrganizationProfileSerializer


class ProducerProfileViewSet(BaseOrganizationProfileViewSet):
    queryset = ProducerProfile.objects.all()
    serializer_class = ProducerProfileSerializer


class ImporterProfileViewSet(BaseOrganizationProfileViewSet):
    queryset = ImporterProfile.objects.all()
    serializer_class = ImporterProfileSerializer


class PackhouseExporterProfileViewSet(BaseOrganizationProfileViewSet):
    queryset = PackhouseExporterProfile.objects.all()
    serializer_class = PackhouseExporterProfileSerializer


class TradeExporterProfileViewSet(BaseOrganizationProfileViewSet):
    queryset = TradeExporterProfile.objects.all()
    serializer_class = TradeExporterProfileSerializer
