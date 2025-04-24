from rest_framework import viewsets
from rest_framework.exceptions import NotAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import PaymentKindAdditionalInputSerializer
from packhouses.packhouse_settings.models import PaymentKindAdditionalInput
from packhouses.packhouse_settings.models import PaymentKind
from rest_framework.response import Response



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

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        requires_bank = False
        payment_kind_id = request.query_params.get('payment_kind')
        if payment_kind_id:
            try:
                pk = PaymentKind.objects.get(id=payment_kind_id)
                requires_bank = pk.requires_bank
            except PaymentKind.DoesNotExist:
                pass

        return Response({
            'requires_bank': requires_bank,
            'additional_inputs': serializer.data
        })


