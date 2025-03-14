from django import forms
from django.contrib import admin
from packhouses.catalogs.models import Product
from common.base.models import ProductKind
from common.profiles.models import OrganizationProfile
from common.base.mixins import ByOrganizationAdminMixin, ByProductForOrganizationAdminMixin
from .models import (Certifications, CertificationsDocuments)
from common.utils import is_instance_used
from common.base.models import RequirementCertification, CertificationEntity
from django.db.models import Q

class CertificationsDocumentsInline(admin.TabularInline):
    model = CertificationsDocuments
    extra = 1

@admin.register(Certifications)
class CertificationsAdmin(ByOrganizationAdminMixin, admin.ModelAdmin):
    list_display = ('certification_entity',)
    list_filter = ['certification_entity']
    exclude = ['organization']
    inlines = [CertificationsDocumentsInline]
    readonly_fields = ['requirement_certifications_list']

    def requirement_certifications_list(self, obj):
        print(f"llego")
        """Muestra los requisitos asociados con enlaces de descarga."""
        if not obj or not obj.certification_entity:
            print(f"{obj}")
            print(f"{obj.certification_entity}")
            return "-"

        requirements = RequirementCertification.objects.filter(certification_entity=obj.certification_entity)
        print(f"{requirements}")
        if not requirements.exists():
            return "No hay requisitos asociados."

        links = [
            format_html('<a href="{}" target="_blank">{}</a>', req.route.url, req.name)
            if req.route else req.name
            for req in requirements
        ]
        return format_html('<br>'.join(links))

    requirement_certifications_list.short_description = "Requisitos de Certificación"

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['certification_entity', 'requirement_certifications_list']
        return ['requirement_certifications_list']

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['certification_entity']
        return []

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "certification_entity":
            this_organization = request.organization 
            organization_country = OrganizationProfile.objects.filter(organization=this_organization).values_list('country', flat=True).first()
            product_kinds = Product.objects.filter(organization=this_organization).values_list('kind', flat=True)
            existing_certifications = Certifications.objects.filter(organization=this_organization).values_list('certification_entity', flat=True)

            kwargs["queryset"] = CertificationEntity.objects.filter(product_kind__id__in=product_kinds).filter(Q(country__isnull=True) | Q(country=organization_country)).exclude(id__in=existing_certifications)
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    