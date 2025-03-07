from django.contrib import admin
from .models import IncomingProduct
from common.base.mixins import (ByOrganizationAdminMixin)
from django import forms

# Register your models here.

class IncomingProductForm(forms.ModelForm):
    class Meta:
        model = IncomingProduct
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aquí definimos el formato: nombre: producto-tipo
        self.fields['harvest'].label_from_instance = lambda obj: f"Harvest {obj.ooid}: {obj.harvest_date} - {obj.product} - {obj.orchard}"

@admin.register(IncomingProduct)
class IncomingProductAdmin(ByOrganizationAdminMixin):
    form = IncomingProductForm

    class Media:
        js = ('js/admin/forms/packhouses/receiving/incoming_product.js',)


