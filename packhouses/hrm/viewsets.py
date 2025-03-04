from rest_framework import viewsets
from rest_framework.exceptions import NotAuthenticated
from .models import JobPosition
from .serializers import JobPositionSerializer

class JobPositionViewSet(viewsets.ModelViewSet):
    serializer_class = JobPositionSerializer
    filterset_fields = ['organization', 'is_enabled']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        return JobPosition.objects.filter(organization=self.request.organization)
