import django_filters
from .models import OrchardCertificationVerifier

class OrchardCertificationVerifierFilter(django_filters.FilterSet):
    id = django_filters.BaseInFilter(field_name='id', lookup_expr='in')

    class Meta:
        model = OrchardCertificationVerifier
        fields = ['id', 'organization', 'is_enabled']
