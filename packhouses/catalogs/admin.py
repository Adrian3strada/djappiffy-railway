from django.contrib import admin
from .models import Market, KGCostMarket
from django_ckeditor_5.widgets import CKEditor5Widget
from django import forms

# Register your models here.


class KGCostMarketInline(admin.TabularInline):
    model = KGCostMarket
    extra = 0


class MarketAdminForm(forms.ModelForm):

    class Meta:
        model = Market
        fields = '__all__'
        widgets = {
            'address_label': CKEditor5Widget(),  # Usa CKEditor para el campo 'address'
        }


@admin.register(Market)
class MarketAdmin(admin.ModelAdmin):
    form = MarketAdminForm
    inlines = [KGCostMarketInline]
