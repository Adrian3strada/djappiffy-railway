from django.contrib import admin
from .models import TaxRegime, LegalEntity, BillingSerie

# Register your models here.


admin.site.register(TaxRegime)



class BillingSerieInline(admin.TabularInline):
    model = BillingSerie
    extra = 0


@admin.register(LegalEntity)
class LegalEntityAdmin(admin.ModelAdmin):
    inlines = [BillingSerieInline]
