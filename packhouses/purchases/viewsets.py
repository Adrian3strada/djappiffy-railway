from rest_framework import viewsets
from rest_framework.exceptions import NotAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import PaymentKindAdditionalInputSerializer
from packhouses.packhouse_settings.models import PaymentKindAdditionalInput

class PaymentKindAdditionalInputViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentKindAdditionalInputSerializer
    queryset = PaymentKindAdditionalInput.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['payment_kind', 'is_enabled',]
    pagination_class = None

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            raise NotAuthenticated()
        return super().get_queryset()
