from django import forms
from django.contrib import admin
from packhouses.catalogs.models import Product
from common.base.models import ProductKind
from .models import (CertificationCatalog, RequirementsCertification, Certifications)#, CertificationProducts, Certifications CertificationsDocuments)

class RequirementsCertificationInline(admin.TabularInline):
    model = RequirementsCertification
    extra = 0

@admin.register(CertificationCatalog)
class CertificationCatalogAdmin(admin.ModelAdmin):
    list_display = ('certifier', 'certification', 'is_enabled')
    list_filter = ['certifier', 'certification', 'is_enabled']
    inlines = [RequirementsCertificationInline]


# class CertificationsDocumentsInline(admin.TabularInline):
#     model = CertificationsDocuments
#     extra = 1

@admin.register(Certifications)
class CertificationsAdmin(admin.ModelAdmin):
    list_display = ('certification_catalog',)
#     list_filter = ['certification_catalog']
    # inlines = [CertificationsDocumentsInline]