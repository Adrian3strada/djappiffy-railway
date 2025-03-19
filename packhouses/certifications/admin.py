from django import forms
from django.contrib import admin
from packhouses.catalogs.models import Product
from common.base.models import ProductKind
from common.profiles.models import OrganizationProfile
from common.base.mixins import ByOrganizationAdminMixin
from .models import (Certifications, CertificationsDocuments)
from common.utils import is_instance_used
from common.base.models import RequirementCertification, CertificationEntity
from django.db.models import Q
from django.utils.html import format_html
from django.urls import reverse
import nested_admin

# class RequirementCertificationInline(admin.TabularInline):
    # model = RequirementCertification
    # extra = 0  # No agrega filas vacías automáticamente
    # readonly_fields = ('name', 'route', 'is_enabled')  # Solo lectura
    # can_delete = False  # No se pueden eliminar desde aquí

    # def has_add_permission(self, request, obj=None):
    #     return False  # No permite agregar desde esta vista

    # def get_queryset(self, request):
    #     """
    #     Filtra los requerimientos solo para el CertificationEntity del objeto actual.
    #     """
    #     qs = super().get_queryset(request)
    #     if request.resolver_match.kwargs.get('object_id'):  # Si estamos editando un objeto existente
    #         certification = Certifications.objects.filter(id=request.resolver_match.kwargs['object_id']).first()
    #         if certification:
    #             return qs.filter(certification_entity=certification.certification_entity)
    #     return qs.none()


class CertificationsDocumentsInline(admin.TabularInline):
    model = CertificationsDocuments
    extra = 1

@admin.register(Certifications)
class CertificationsAdmin(ByOrganizationAdminMixin, admin.ModelAdmin):
    list_display = ('certification_entity',)
    list_filter = ['certification_entity']
    exclude = ['organization']
    # inlines = [CertificationsDocumentsInline]
    # inlines = [RequirementCertificationInline]

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
    