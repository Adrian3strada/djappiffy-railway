from django.contrib import admin
from common.base.mixins import ByOrganizationAdminMixin
from .models import LegalEntity, BillingSerie, ExchangeRate

# Register your models here.

class BillingSerieInline(admin.TabularInline):
    model = BillingSerie
    extra = 0

@admin.register(LegalEntity)
class LegalEntityAdmin(admin.ModelAdmin):
    inlines = [BillingSerieInline]

@admin.register(ExchangeRate)
class ExchangeRateAdmin(ByOrganizationAdminMixin, admin.ModelAdmin):
    list_display = ('currency_unit', 'currency', 'exchange_rate_value', 'target_currency', 'registration_date', 'is_enabled')
    list_filter = ['currency_unit', 'currency', 'exchange_rate_value', 'target_currency', 'registration_date', 'is_enabled']
    exclude = ['organization']

    class Media:
        js = ('js/admin/forms/common/exchange_rate.js',)

