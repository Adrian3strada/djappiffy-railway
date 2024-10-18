from common.base.router import drf_router
from .viewsets import ExportRequestViewSet, ExportRequestProducerViewSet, ExportRequestPaymentViewSet

# write your urls here

drf_router.register(r'rest/v1/exporters/export-requests', ExportRequestViewSet, basename='export-requests')
drf_router.register(r'rest/v1/exporters/export-request-producers', ExportRequestProducerViewSet, basename='export-request-producers')
drf_router.register(r'rest/v1/exporters/export-request-payments', ExportRequestPaymentViewSet, basename='export-request-payments')

urlpatterns = drf_router.urls
