from django.contrib import admin
from .models import TaxRegime, LegalEntityCategory, LegalEntity, BillingSerie

# Register your models here.


admin.site.register(TaxRegime)


@admin.register(LegalEntityCategory)
class LegalEntityCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'country']
    search_fields = ['name',]
    list_filter = ['country']


class BillingSerieInline(admin.TabularInline):
    model = BillingSerie
    extra = 0


@admin.register(LegalEntity)
class LegalEntityAdmin(admin.ModelAdmin):
    inlines = [BillingSerieInline]
