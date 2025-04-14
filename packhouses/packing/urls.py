from django.urls import path
from .views import generate_label_pdf, discard_labels, generate_pending_label_pdf

urlpatterns = [
    path("generate_label/<int:employee_id>/", generate_label_pdf, name="generate_label"),
    path("generate_pending_labels/<int:employee_id>/", generate_pending_label_pdf, name="generate_pending_labels"),
    path("discard_labels/<int:employee_id>/", discard_labels, name="discard_labels"),
]