# admin_mixins.py
from django.contrib import admin


class ByOrganizationAdminMixin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if hasattr(request, 'organization'):
            return qs.filter(organization=request.organization)
        return qs

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            if hasattr(request, 'organization'):
                obj.organization = request.organization
        super().save_model(request, obj, form, change)


# TODO: creo que esta puede estar mal... revisar
class ByProductAdminMixin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if hasattr(request, 'product'):
            return qs.filter(product=request.product, is_enabled=True)
        return qs
