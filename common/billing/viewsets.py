from rest_framework import viewsets
from .serializers import LegalEntityCategorySerializer
from .models import LegalEntityCategory

# ViewSets define the view behavior.


class LegalEntityCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = LegalEntityCategorySerializer
    pagination_class = None
    queryset = LegalEntityCategory.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        country_id = self.request.GET.get('country')
        if country_id:
            queryset = queryset.filter(country_id=country_id)
        return queryset


