from django.urls import path
from .views import generate_label_pdf

urlpatterns = [
    path("generate_label/<int:employee_id>/", generate_label_pdf, name="generate_label"),
]