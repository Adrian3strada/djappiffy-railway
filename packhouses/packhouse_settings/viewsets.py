from rest_framework import viewsets
from rest_framework.exceptions import NotAuthenticated
from django_filters import rest_framework as drf_filters
from .serializers import OrchardCertificationKindSerializer, OrchardCertificationVerifierSerializer
from .models import OrchardCertificationKind, OrchardCertificationVerifier
from .filters import OrchardCertificationVerifierFilter


class OrchardCertificationKindViewSet(viewsets.ModelViewSet):
    serializer_class = OrchardCertificationKindSerializer
    filterset_fields = ['organization','is_enabled']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        if user.is_superuser:
            return OrchardCertificationKind.objects.all()

        user_organizations = user.organizations_organization.all()
        return OrchardCertificationKind.objects.filter(organization__in=user_organizations)


class OrchardCertificationVerifierViewSet(viewsets.ModelViewSet):
    serializer_class = OrchardCertificationVerifierSerializer
    filter_backends = (drf_filters.DjangoFilterBackend,)
    filterset_class = OrchardCertificationVerifierFilter
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        if user.is_superuser:
            return OrchardCertificationVerifier.objects.all()

        user_organizations = user.organizations_organization.all()
        return OrchardCertificationVerifier.objects.filter(organization__in=user_organizations)
