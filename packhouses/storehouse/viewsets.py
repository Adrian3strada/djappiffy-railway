from rest_framework import viewsets
from rest_framework.exceptions import NotAuthenticated
from .serializers import PurchaseOrderSupplySerializer

from django_filters.rest_framework import DjangoFilterBackend
from packhouses.purchases.models import PurchaseOrderSupply

class PurchaseOrderSupplyViewSet(viewsets.ModelViewSet):
    serializer_class = PurchaseOrderSupplySerializer
    filterset_fields = ['purchase_order']  # Filtra por purchase_order
    pagination_class = None  # Desactiva la paginación

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        # Filtra los PurchaseOrderSupply por purchase_order_id
        purchase_order_id = self.request.query_params.get('purchase_order', None)
        if purchase_order_id:
            return PurchaseOrderSupply.objects.filter(purchase_order_id=purchase_order_id)
        return PurchaseOrderSupply.objects.none()
