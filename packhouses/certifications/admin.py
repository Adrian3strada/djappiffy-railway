from django import forms
from django.contrib import admin
from packhouses.catalogs.models import Product
from common.base.models import ProductKind
from .models import (CertificationCatalog, RequirementsCertification, CertificationProducts, Certifications, CertificationsDocuments)

class RequirementsCertificationInline(admin.TabularInline):
    model = RequirementsCertification
    extra = 1

# -------------------------

class CertificationProductsForm(forms.ModelForm):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):

        if db_field.name == "product":
            if request.POST:
                product_id = request.POST.get('product_kind') if request.POST else None


            if product_kind_id:
                kwargs["queryset"] = Product.objects.filter(product_kind_id=product_kind_id, is_enabled=True)
            else:
                kwargs["queryset"] = Product.objects.none()

            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda item: item.name
            return formfield

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/packhouses/certifications/products_kind.js',)


class CertificationProductsInline(admin.TabularInline):
    model = CertificationProducts
    extra = 1
    form = CertificationProductsForm 

@admin.register(CertificationCatalog)
class CertificationCatalogAdmin(admin.ModelAdmin):
    list_display = ('certifier', 'certification', 'is_enabled')
    list_filter = ['certifier', 'certification', 'is_enabled']
    inlines = [RequirementsCertificationInline, CertificationProductsInline]

# class CertificationsDocumentsInline(admin.TabularInline):
#     model = CertificationsDocuments
#     extra = 1

# @admin.register(Certifications)
# class CertificationsAdmin(admin.ModelAdmin):
#     list_display = ('certification', 'registration_date', 'expiration_date', 'certification_catalog')
#     list_filter = ['certification', 'registration_date', 'expiration_date', 'certification_catalog']
    # inlines = [CertificationsDocumentsInline]