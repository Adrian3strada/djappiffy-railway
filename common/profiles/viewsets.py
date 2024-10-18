
from rest_framework import mixins, viewsets, permissions
from .serializers import UserProfileSerializer, OrganizationProfileSerializer
from .models import UserProfile, OrganizationProfile

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
