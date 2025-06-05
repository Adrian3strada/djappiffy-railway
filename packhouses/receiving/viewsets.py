from rest_framework import viewsets
from rest_framework.exceptions import NotAuthenticated
from .serializers import BatchSerializer
from .models import Batch

class BatchViewSet(viewsets.ModelViewSet):
    serializer_class = BatchSerializer
    queryset = Batch.objects.all()
    filterset_fields = ['id', 'status',]
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()
        return super().get_queryset()
