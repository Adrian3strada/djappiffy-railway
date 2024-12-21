from rest_framework import viewsets
from rest_framework.exceptions import NotAuthenticated
from .serializers import OrchardCertificationKindSerializer
from .models import OrchardCertificationKind


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

