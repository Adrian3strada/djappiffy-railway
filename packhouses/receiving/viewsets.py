from rest_framework import viewsets
from rest_framework.exceptions import NotAuthenticated
from .serializers import BatchSerializer
from .models import Batch


class BatchViewSet(viewsets.ModelViewSet):
    serializer_class = BatchSerializer
    filterset_fields = ['id','ooid', 'status', 'is_available_for_processing']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        queryset = Batch.objects.filter(organization=self.request.organization)
        return queryset
