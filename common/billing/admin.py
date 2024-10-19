from django.contrib import admin
from .models import TaxRegime, LegalEntityCategory, LegalEntity, BillingSerie

# Register your models here.


admin.site.register(TaxRegime)
admin.site.register(LegalEntityCategory)


class BillingSerieInline(admin.TabularInline):
    model = BillingSerie
    extra = 0


@admin.register(LegalEntity)
class LegalEntityAdmin(admin.ModelAdmin):
    inlines = [BillingSerieInline]
