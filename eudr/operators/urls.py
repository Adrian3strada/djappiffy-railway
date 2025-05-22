from django.urls import path, include
from common.base.router import drf_router
from .viewsets import OperatorParcelViewSet, ProductionIntervalViewSet, LegalComplianceViewSet

# write your urls here

urlpatterns = []

drf_router.register(r'rest/v1/eudr/operator/parcel', OperatorParcelViewSet, basename='operator_parcel')
drf_router.register(r'rest/v1/eudr/operator/production-interval', ProductionIntervalViewSet, basename='production_interval')
drf_router.register(r'rest/v1/eudr/operator/legal-compliance', LegalComplianceViewSet, basename='legal_compliance')

urlpatterns += drf_router.urls
