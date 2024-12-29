# admin_mixins.py

from django.shortcuts import get_object_or_404
from organizations.models import Organization

class OrganizationAdminMixin:
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if hasattr(request, 'organization'):
            return qs.filter(organization=request.organization)
        return qs

    def save_model(self, request, obj, form, change):
        if hasattr(request, 'organization'):
            obj.organization = request.organization
        super().save_model(request, obj, form, change)
