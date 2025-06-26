from rest_framework import viewsets
from rest_framework.exceptions import NotAuthenticated
from .serializers import PackingPalletSerializer
from .models import PackingPallet

# create your viewsets here.


class PackingPalletViewSet(viewsets.ModelViewSet):
    serializer_class = PackingPalletSerializer
    filterset_fields = ['market', 'product', 'product_sizes', 'status']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()

        queryset = PackingPallet.objects.filter(product__organization=self.request.organization)

        return queryset
