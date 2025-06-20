from common.base.router import drf_router
from .viewsets import (
    OrchardCertificationKindViewSet,
    OrchardCertificationVerifierViewSet,
    OrchardCertificationKindForEudrViewSet,
    OrchardCertificationVerifierForEudrViewSet
)

urlpatterns = []

drf_router.register(r'rest/v1/packhouse-settings/orchard-certification-kind', OrchardCertificationKindViewSet, basename='packhouse-settings_orchard-certification-kind')
drf_router.register(r'rest/v1/packhouse-settings/orchard-certification-verifier', OrchardCertificationVerifierViewSet, basename='packhouse-settings_orchard-certification-verifier')
drf_router.register(
    r'rest/v1/packhouse-settings/orchard-certification-kind-for-eudr',
    OrchardCertificationKindForEudrViewSet,
    basename='packhouse-settings_orchard-certification-kind-for-eudr'
)
drf_router.register(
    r'rest/v1/packhouse-settings/orchard-certification-verifier-for-eudr',
    OrchardCertificationVerifierForEudrViewSet,
    basename='packhouse-settings_orchard-certification-verifier-for-eudr'
)

urlpatterns += drf_router.urls
