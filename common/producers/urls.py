from common.base.router import drf_router
from .viewsets import ProducerViewSet, CertificationViewSet

# write your urls here

drf_router.register(r'rest/v1/producers/producers', ProducerViewSet, basename='producerss')
drf_router.register(r'rest/v1/producers/productores', ProducerViewSet, basename='productores')
drf_router.register(r'rest/v1/producers/certificates', CertificationViewSet, basename='certificates')

urlpatterns = drf_router.urls
