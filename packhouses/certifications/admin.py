from django import forms
from django.contrib import admin
from packhouses.catalogs.models import Product
from common.base.models import ProductKind
from common.profiles.models import OrganizationProfile
from common.base.mixins import ByOrganizationAdminMixin
from .models import Certification, CertificationDocument, Format
from common.utils import is_instance_used
from common.base.models import CertificationEntity
from django.db.models import Q
from django.utils.html import format_html
from django.urls import reverse

class CertificationDocumentInline(admin.TabularInline):
    model = CertificationDocument
    extra = 1

class FormatInline(admin.TabularInline):
    model = Format
    extra = 1

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def document_link(self, obj):
        certification_format = obj.certification_format
        if certification_format.route:
            return format_html(
                '<a href="{}" download><i class="fa-solid fa-download" aria-hidden="true"></i></a>', 
                certification_format.route.url
            )
        return "No disponible"

    document_link.short_description = "Acciones"
    readonly_fields = ('document_link',)

    def get_list_display(self, request):
        return ('document_link',)


@admin.register(Certification)
class CertificationAdmin(ByOrganizationAdminMixin, admin.ModelAdmin):
    list_display = ('certification_entity',)
    list_filter = ['certification_entity']
    exclude = ['organization']
    inlines = [FormatInline, CertificationDocumentInline]

    def get_inlines(self, request, obj=None):
        inlines = []
        if obj:  # Si el objeto ya está creado (no es un nuevo objeto)
            inlines = [FormatInline, CertificationDocumentInline]
        return inlines

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "certification_entity":
            this_organization = request.organization 
            organization_country = OrganizationProfile.objects.filter(organization=this_organization).values_list('country', flat=True).first()
            product_kinds = Product.objects.filter(organization=this_organization).values_list('kind', flat=True)
            existing_certifications = Certification.objects.filter(organization=this_organization).values_list('certification_entity', flat=True)

            obj_id = request.resolver_match.kwargs.get("object_id")
            current_certification_entity = None

            if obj_id:
                current_certification_entity = Certification.objects.get(id=obj_id).certification_entity_id
                if current_certification_entity:
                    kwargs["queryset"] = CertificationEntity.objects.filter(id=current_certification_entity)
                else:
                    kwargs["queryset"] = CertificationEntity.objects.none()  # En caso de error, que no muestre opciones

            else:
                kwargs["queryset"] = CertificationEntity.objects.filter(
                    Q(product_kind__id__in=product_kinds) & 
                    (Q(country__isnull=True) | Q(country=organization_country))
                ).exclude(id__in=existing_certifications)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        form.base_fields['certification_entity'].widget.can_add_related = False
        form.base_fields['certification_entity'].widget.can_change_related = False
        form.base_fields['certification_entity'].widget.can_delete_related = False

        return form
    