from django import forms
from django.contrib import admin
from packhouses.catalogs.models import Product
from common.base.models import ProductKind
from common.base.mixins import ByOrganizationAdminMixin, ByProductForOrganizationAdminMixin
from .models import (Certifications)
from common.utils import is_instance_used
from common.base.models import RequirementCertification, CertificationEntity

# # # # class CertificationsDocumentsInline(admin.TabularInline):
# # # #     model = CertificationsDocuments
# # # #     extra = 1

@admin.register(Certifications)
class CertificationsAdmin(ByOrganizationAdminMixin, admin.ModelAdmin):
    list_display = ('certification_entity',)
    list_filter = ['certification_entity']
    exclude = ['organization']
    # inlines = [RequirementCertificationInline]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['certification_entity']
        return []

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "certification_entity":
            this_organization = request.organization 
            product_kinds = Product.objects.filter(organization=this_organization).values_list('kind', flat=True)
            existing_certifications = Certifications.objects.filter(organization=this_organization).values_list('certification_entity', flat=True)

            kwargs["queryset"] = CertificationEntity.objects.filter(product_kind__id__in=product_kinds).exclude(id__in=existing_certifications)
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    