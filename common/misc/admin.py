from django.contrib import admin
from .models import TaxRegimeCategory, TaxRegime, LegalEntityCategory, LegalEntity

# Register your models here.

admin.site.register(TaxRegimeCategory)
admin.site.register(TaxRegime)
admin.site.register(LegalEntityCategory)
admin.site.register(LegalEntity)
