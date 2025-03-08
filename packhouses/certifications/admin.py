
from django.contrib import admin
from .models import (CertificationCatalog, CertificationDocuments, CertificationProducts, Certifications)

class CertificationDocumentsInline(admin.TabularInline):
    model = CertificationDocuments
    extra = 1

class CertificationProductsInline(admin.TabularInline):
    model = CertificationProducts
    extra = 1

@admin.register(CertificationCatalog)
class CertificationCatalogAdmin(admin.ModelAdmin):
    list_display = ('certifier', 'certification', 'is_enabled')
    list_filter = ['certifier', 'certification', 'is_enabled']
    inlines = [CertificationDocumentsInline, CertificationProductsInline]

@admin.register(Certifications)
class CertificationsAdmin(admin.ModelAdmin):
    list_display = ('certification', 'registration_date', 'expiration_date', 'certification_catalog')
    list_filter = ['certification', 'registration_date', 'expiration_date', 'certification_catalog']