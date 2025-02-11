from django.contrib import admin
from .models import LegalEntity, BillingSerie

# Register your models here.


class BillingSerieInline(admin.TabularInline):
    model = BillingSerie
    extra = 0


@admin.register(LegalEntity)
class LegalEntityAdmin(admin.ModelAdmin):
    inlines = [BillingSerieInline]
