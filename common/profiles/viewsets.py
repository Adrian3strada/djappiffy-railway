from rest_framework import viewsets
from .models import (UserProfile, OrganizationProfile, ProducerProfile, ImporterProfile, PackhouseExporterProfile,
                     TradeExporterProfile)
from .serializers import (UserProfileSerializer, ProducerProfileSerializer,
                          ImporterProfileSerializer, PackhouseExporterProfileSerializer, TradeExporterProfileSerializer,
                          OrganizationProfilePolymorphicSerializer)
from .permissions import IsOrganizationMember
from organizations.models import OrganizationUser


class BaseOrganizationProfileViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOrganizationMember]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return self.queryset
        return self.queryset.filter(organization__organization_users__in=OrganizationUser.objects.filter(user=user))

    def perform_create(self, serializer):
        products_data = self.request.data.pop('products', [])
        del serializer.validated_data['products']
        instance = serializer.save()
        instance.product_kinds.set(products_data)

    def perform_update(self, serializer):
        products_data = self.request.data.pop('products', [])
        del serializer.validated_data['products']
        instance = serializer.save()
        instance.product_kinds.set(products_data)
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
    serializer_class = OrganizationProfilePolymorphicSerializer


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
