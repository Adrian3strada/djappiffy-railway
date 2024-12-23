from common.base.router import drf_router
from .viewsets import OrchardCertificationKindViewSet, OrchardCertificationVerifierViewSet

urlpatterns = []

drf_router.register(r'rest/v1/packhouse-settings/orchard-certification-kind', OrchardCertificationKindViewSet, basename='packhouse-settings_orchard-certification-kind')
drf_router.register(r'rest/v1/packhouse-settings/orchard-certification-verifier', OrchardCertificationVerifierViewSet, basename='packhouse-settings_orchard-certification-verifier')

urlpatterns += drf_router.urls
