from django import forms
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import StorehouseEntrySupply
from packhouses.purchase.models import PurchaseOrderSupply


class StorehouseEntrySupplyInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Obtener el ID de la orden de compra
        purchase_order_id = None
        if self.data.get('purchase_order'):
            purchase_order_id = self.data.get('purchase_order')
        elif self.instance and self.instance.purchase_order_id:
            purchase_order_id = self.instance.purchase_order_id

        is_closed = False
        if purchase_order_id:
            # Determinar el status:
            if self.instance and self.instance.purchase_order_id:
                is_closed = (self.instance.purchase_order.status == "closed")
            else:
                # Si no tenemos instancia, lo obtenemos de la BD
                try:
                    from packhouses.purchase.models import PurchaseOrder
                    po = PurchaseOrder.objects.get(pk=purchase_order_id)
                    is_closed = (po.status == "closed")
                except PurchaseOrder.DoesNotExist:
                    is_closed = False

        if is_closed:
            # Si la orden está cerrada, removemos el campo de cada formulario
            for form in self.forms:
                form.fields.pop('purchase_order_supply', None)
        else:
            # Si no está cerrada, configuramos el queryset del campo
            if purchase_order_id:
                qs = PurchaseOrderSupply.objects.filter(purchase_order=purchase_order_id)
                for form in self.forms:
                    if 'purchase_order_supply' in form.fields:
                        form.fields['purchase_order_supply'].queryset = qs


