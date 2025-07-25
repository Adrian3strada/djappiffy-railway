from django import forms
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import StorehouseEntrySupply, AdjustmentInventory, InventoryTransaction, StorehouseEntry
from packhouses.purchases.models import PurchaseOrderSupply, PurchaseOrder
from decimal import Decimal
from django.db.models import DecimalField, Value, Sum, F, Subquery, OuterRef, Q
from django.db.models.functions import Coalesce
from .utils import validate_inventory_availability, get_inventory_balance, get_source_for_quantity_fifo


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
                    from packhouses.purchases.models import PurchaseOrder
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

class AdjustmentInventoryForm(forms.ModelForm):
    """
    Formulario para validar y aplicar ajustes de inventario (entrada o salida).
    """

    class Meta:
        model = AdjustmentInventory
        fields = '__all__'

    def clean(self):
        """
        Valida si hay suficiente inventario para las transacciones de tipo salida.
        """
        cleaned = super().clean()
        supply = cleaned.get('supply')
        qty    = cleaned.get('quantity')
        org    = getattr(self, 'request_organization', None)
        kind   = cleaned.get('transaction_kind')

        if not (supply and qty and org and kind):
            return cleaned

        if kind == 'outbound':
            remaining = validate_inventory_availability(supply, qty, org)
            self.cleaned_data['available_quantity'] = remaining

        return cleaned

    def save(self, commit=True):
        """
        Guarda el AdjustmentInventory y crea los movimientos reales en InventoryTransaction.
        """
        obj = super().save(commit=False)

        if not obj.organization_id:
            obj.organization = getattr(self, 'request_organization', None)

        if commit:
            obj.save()
            self.save_m2m()  # Necesario por consistencia o relaciones manytomany

        # Lógica de transacción de inventario
        kind = obj.transaction_kind
        supply = obj.supply
        qty = obj.quantity
        org = obj.organization
        user = getattr(self, '_request_user', None)
        if not user:
            raise ValidationError(_("Unable to determine the creator user for this transaction."))

        if kind == 'inbound':
            InventoryTransaction.objects.create(
                supply=supply,
                transaction_kind='inbound',
                transaction_category=obj.transaction_category,
                quantity=qty,
                created_by=user,
                organization=org
            )

        elif kind == 'outbound':
            """
            Se obtienen los movimientos FIFO disponibles para la salida del insumo.
            Se crean transacciones de salida en InventoryTransaction para cada movimiento
            hasta completar la cantidad solicitada.
            """
            fifo_movements = get_source_for_quantity_fifo(supply, qty, org)

            for mov in fifo_movements:
                InventoryTransaction.objects.create(
                    supply=supply,
                    transaction_kind='outbound',
                    transaction_category=obj.transaction_category,
                    quantity=mov['take'],
                    storehouse_entry_supply=mov['entry'].storehouse_entry_supply,
                    created_by=user,
                    organization=org
                )

        return obj

class StorehouseEntryForm(forms.ModelForm):
    class Meta:
        model = StorehouseEntry
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        # Personalizamos el queryset del campo purchase_order
        if 'purchase_order' in self.fields:
            qs = PurchaseOrder.objects.filter(status='ready')
            if request and hasattr(request, 'organization'):
                qs = qs.filter(organization=request.organization)

            # Redefinimos el campo con label personalizado
            self.fields['purchase_order'] = forms.ModelChoiceField(
                queryset=qs,
                label=_("Purchase Order"),
                widget=self.fields['purchase_order'].widget
            )
            self.fields['purchase_order'].label_from_instance = lambda obj: f"{obj.ooid} - {obj.provider.name}"
