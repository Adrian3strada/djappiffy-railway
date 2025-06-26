from django.urls import path
from .views import generate_label_pdf, discard_labels, generate_pending_label_pdf
from common.base.router import drf_router
from .viewsets import PackingPalletViewSet

urlpatterns = [
    path("dadmin/packing/packeremployee/generate_label/<int:employee_id>/", generate_label_pdf, name="generate_label"),
    path("dadmin/packing/packeremployee/generate_pending_labels/<int:employee_id>/", generate_pending_label_pdf, name="generate_pending_labels"),
    path("dadmin/packing/packeremployee/discard_labels/<int:employee_id>/", discard_labels, name="discard_labels"),
]

drf_router.register(r'rest/v1/packing/packing-pallet', PackingPalletViewSet, basename='packing_pallet')

urlpatterns += drf_router.urls
