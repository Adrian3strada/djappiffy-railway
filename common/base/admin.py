from django.contrib import admin

from organizations.admin import OrganizationAdmin
from organizations.models import Organization

from .models import ProductKind


@admin.register(ProductKind)
class ProductKindAdmin(admin.ModelAdmin):
    pass


class CustomOrganizationAdmin(OrganizationAdmin):
    list_display = ["id", "name", "slug", "created", "modified", "is_active"]
    ordering = ["id"]

admin.site.unregister(Organization)
admin.site.register(Organization, CustomOrganizationAdmin)
