from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import (Requisition, PurchaseOrder, PurchaseOrderPayment,RequisitionSupply, ServiceOrder,
                    ServiceOrderPayment, PurchaseMassPayment, FruitPurchaseOrderReceipt, FruitPurchaseOrderPayment
                     )
from django.forms.models import ModelChoiceField
import json
from django.utils.safestring import mark_safe
from packhouses.catalogs.models import Supply, Provider
from django.db import models
from decimal import Decimal, ROUND_HALF_UP
import datetime
from common.widgets import CustomFileDisplayWidget
from django.forms.models import BaseInlineFormSet



class RequisitionForm(forms.ModelForm):
    class Meta:
        model = Requisition
        fields = '__all__'

    question_button_text = _("How would you like to proceed?")
    confirm_button_text = _("Save and send to purchases")
    deny_button_text = _("Only save")
    cancel_button_text = _("Cancel")

    save_and_send = forms.BooleanField(
        label=_("Save and send to Purchase Operations Department"),
        required=False,
        widget=forms.HiddenInput(attrs={
            'data-question': question_button_text,
            'data-confirm': confirm_button_text,
            'data-deny': deny_button_text,
            'data-cancel': cancel_button_text
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        requisition_supplies = self.data.getlist('requisitionsupply_set-TOTAL_FORMS', [])
        if not requisition_supplies or int(requisition_supplies[0]) < 1:
            raise ValidationError(_("You must add at least one supply to the requisition."))


        return cleaned_data

class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = '__all__'

    question_button_text = _("How would you like to proceed?")
    confirm_button_text = _("Save and send to Storehouse")
    deny_button_text = _("Only save")
    cancel_button_text = _("Cancel")

    save_and_send = forms.BooleanField(
        label=_("Save and send to Storehouse"),
        required=False,
        widget=forms.HiddenInput(attrs={
            'data-question': question_button_text,
            'data-confirm': confirm_button_text,
            'data-deny': deny_button_text,
            'data-cancel': cancel_button_text
        })
    )

    def clean(self):
        cleaned_data = super().clean()

        # ⚡ Validación temprana para evitar balances imposibles
        purchase_order = self.instance

        # Si no se ha creado todavía, no podemos hacer balance
        if not purchase_order.pk:
            return cleaned_data

        balance_data = purchase_order.simulate_balance()
        if balance_data['balance'] < 0:
            raise ValidationError(_(
                f"Cannot save this purchases order because the balance would be negative (${balance_data['balance']}). "
                f"Supplies: ${balance_data['supplies_total']}, "
                f"Taxes: ${balance_data['tax_amount']}, "
                f"Charges: ${balance_data['charges_total']}, "
                f"Payments: ${balance_data['payments_total']}, "
                f"Deductions: ${balance_data['deductions_total']}."
            ))

        return cleaned_data


class PurchaseOrderPaymentForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderPayment
        fields = ('payment_date', 'payment_kind', 'amount', 'bank', 'proof_of_payment', 'comments', 'additional_inputs')
        widgets = {
            'additional_inputs': forms.HiddenInput(),
            'proof_of_payment': CustomFileDisplayWidget()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = self.instance

        # Si el pago ya está registrado, todos los campos se deshabilitan
        if instance and instance.pk:

            for field in self.fields:
                self.fields[field].disabled = True
                self.fields[field].widget.attrs['class'] = self.fields[field].widget.attrs.get('class',
                                                                                               '') + ' readonly-field'

            if 'payment_date' in self.fields:
                self.fields['payment_date'].widget = forms.TextInput(attrs={
                    'readonly': 'readonly',
                    'class': 'readonly-field'
                })

            if instance.additional_inputs:
                self.fields['additional_inputs'].initial = json.dumps(instance.additional_inputs)

        # Deshabilitar los controles relacionados (add, edit, delete) en ForeignKeys
        for field_name in ['payment_kind', 'bank']:
            if hasattr(self.fields[field_name].widget, 'can_add_related'):
                self.fields[field_name].widget.can_add_related = False
                self.fields[field_name].widget.can_change_related = False
                self.fields[field_name].widget.can_delete_related = False
                self.fields[field_name].widget.can_view_related = False

        # Asegurarse de que `bank` no sea obligatorio por defecto
        self.fields['bank'].required = False

    def clean(self):
        cleaned_data = super().clean()
        payment_kind = cleaned_data.get('payment_kind')
        bank = cleaned_data.get('bank')

        if payment_kind and getattr(payment_kind, 'requires_bank', False) and not bank:
            self.add_error('bank', _("This field is required for the selected payment kind."))

        return cleaned_data


class RequisitionSupplyForm(forms.ModelForm):
    class Meta:
        model = RequisitionSupply
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        supply = None
        # Si la instancia ya existe, obtenemos el supply directamente
        if self.instance and self.instance.pk:
            supply = self.instance.supply
        else:
            # Si es una nueva instancia, intentamos obtener el supply desde los datos iniciales
            if 'supply' in self.data:
                try:
                    supply_id = int(self.data.get('supply'))
                    supply = Supply.objects.get(pk=supply_id)
                except (ValueError, Supply.DoesNotExist):
                    pass
            elif 'supply' in self.initial:
                try:
                    supply = Supply.objects.get(pk=self.initial.get('supply'))
                except Supply.DoesNotExist:
                    pass

        if supply:
            # A partir del supply, obtenemos las unidades permitidas de su SupplyKind (campo ManyToManyField)
            requested_units = supply.kind.requested_unit_category.all()
            choices = [(unit.pk, unit.name) for unit in requested_units]
            self.fields['unit_category'].choices = choices
        else:
            # En caso de no tener supply definido, dejamos el campo sin opciones
            self.fields['unit_category'].choices = []


class ServiceOrderForm(forms.ModelForm):
    """
    Formulario para orden de servicio. Solo realiza validaciones de campos individuales
    y no intenta calcular balance ni total_cost. Ese control lo realiza el admin.
    """
    class Meta:
        model = ServiceOrder
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        cost = cleaned_data.get('cost')
        tax = cleaned_data.get('tax')
        batch = cleaned_data.get('batch')

        if cost is not None and cost < 0:
            self.add_error('cost', _("Cost cannot be less than 0."))

        if tax is not None and (tax < 0 or tax > 100):
            self.add_error('tax', _("Tax must be between 0% and 100%."))

        if category == 'for_batch' and not batch:
            self.add_error('batch', _("You must select a batch when category is 'for_batch'."))

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        if instance.category == 'time_period':
            instance.batch = None
        elif instance.category == 'for_batch':
            instance.start_date = datetime.date.today()
            instance.end_date = datetime.date.today()

        if commit:
            instance.save()

        return instance


class ServiceOrderPaymentForm(forms.ModelForm):
    class Meta:
        model = ServiceOrderPayment
        fields = (
            'payment_date',
            'payment_kind',
            'amount',
            'bank',
            'comments',
            'additional_inputs',
        )
        widgets = {
            'additional_inputs': forms.HiddenInput(),
            'proof_of_payment': CustomFileDisplayWidget()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = self.instance

        # Si el pago ya está registrado, todos los campos se deshabilitan
        if instance and instance.pk:

            for field in self.fields:
                self.fields[field].disabled = True
                self.fields[field].widget.attrs['class'] = self.fields[field].widget.attrs.get('class', '') + ' readonly-field'

            if 'payment_date' in self.fields:
                self.fields['payment_date'].widget = forms.TextInput(attrs={
                    'readonly': 'readonly',
                    'class': 'readonly-field'
                })

            if instance.additional_inputs:
                self.fields['additional_inputs'].initial = json.dumps(instance.additional_inputs)


        # Deshabilitar los controles relacionados (add, edit, delete) en ForeignKeys
        for field_name in ['payment_kind', 'bank']:
            if hasattr(self.fields[field_name].widget, 'can_add_related'):
                self.fields[field_name].widget.can_add_related = False
                self.fields[field_name].widget.can_change_related = False
                self.fields[field_name].widget.can_delete_related = False
                self.fields[field_name].widget.can_view_related = False

        # Asegurarse de que `bank` no sea obligatorio por defecto
        self.fields['bank'].required = False

    def clean(self):
        cleaned_data = super().clean()
        payment_kind = cleaned_data.get('payment_kind')
        bank = cleaned_data.get('bank')

        if payment_kind and getattr(payment_kind, 'requires_bank', False) and not bank:
            self.add_error('bank', _("This field is required for the selected payment kind."))

        return cleaned_data


class PurchaseMassPaymentForm(forms.ModelForm):
    class Meta:
        model = PurchaseMassPayment
        fields = ('category', 'provider', 'purchase_order', 'service_order', 'payment_kind',
                  'additional_inputs', 'bank', 'payment_date', 'amount', 'comments')
        widgets = {
            'additional_inputs': forms.HiddenInput(),
            'proof_of_payment': CustomFileDisplayWidget()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = self.instance

        # Modo solo lectura si ya existe
        if instance and instance.pk:
            for field in self.fields:
                self.fields[field].disabled = True
                self.fields[field].widget.attrs['class'] = self.fields[field].widget.attrs.get('class', '') + ' readonly-field'

            if instance.additional_inputs:
                self.fields['additional_inputs'].initial = json.dumps(instance.additional_inputs)

        # Contexto de creación o edición
        is_adding = not instance.pk

        if is_adding:
            # Si estamos creando el Mass Payment, mostramos el balance_payable
            self.fields['purchase_order'].label_from_instance = lambda obj: (
                f"Folio {obj.ooid} - ${obj.balance_payable}"
                if obj.balance_payable > 0
                else f"Folio {obj.ooid}"
            )
            self.fields['service_order'].label_from_instance = lambda obj: (
                f"Folio {obj.id} - ${obj.balance_payable}"
                if obj.balance_payable > 0
                else f"Folio {obj.id}"
            )
        else:
            # Si estamos editando, mostramos el monto pagado individualmente
            def label_from_instance_edit_po(obj):
                payment = PurchaseOrderPayment.objects.filter(
                    purchase_order=obj,
                    mass_payment=instance
                ).first()
                if payment:
                    return f"Folio {obj.ooid} - ${payment.amount}"
                return f"Folio {obj.ooid} - $0.00"

            def label_from_instance_edit_so(obj):
                payment = ServiceOrderPayment.objects.filter(
                    service_order=obj,
                    mass_payment=instance
                ).first()
                if payment:
                    return f"Folio {obj.id} - ${payment.amount}"
                return f"Folio {obj.id} - $0.00"

            # Asignamos la lógica personalizada para mostrar el monto en los labels
            self.fields['purchase_order'].label_from_instance = label_from_instance_edit_po
            self.fields['service_order'].label_from_instance = label_from_instance_edit_so

        for field_name in ['payment_kind', 'bank']:
            if hasattr(self.fields[field_name].widget, 'can_add_related'):
                self.fields[field_name].widget.can_add_related = False
                self.fields[field_name].widget.can_change_related = False
                self.fields[field_name].widget.can_delete_related = False
                self.fields[field_name].widget.can_view_related = False

        self.fields['amount'].widget.attrs['readonly'] = True
        self.fields['amount'].widget.attrs['style'] = 'background-color: #f5f5f5; cursor: not-allowed;'

        self.fields['bank'].required = False

    def clean(self):
        cleaned_data = super().clean()

        payment_kind = cleaned_data.get('payment_kind')
        bank = cleaned_data.get('bank')
        category = cleaned_data.get('category')
        purchase_orders = cleaned_data.get('purchase_order')
        service_orders = cleaned_data.get('service_order')

        total_amount = Decimal('0.00')

        #  Sumar balances según el tipo de orden
        if category == 'purchase_order' and purchase_orders:
            total_amount = sum([
                order.balance_payable for order in purchase_orders if order.balance_payable > 0
            ])
        elif category == 'service_order' and service_orders:
            total_amount = sum([
                order.balance_payable for order in service_orders if order.balance_payable > 0
            ])

        #  Reemplaza el valor manual con el calculado
        cleaned_data['amount'] = total_amount

        #  Validación: si requiere banco y no se puso
        if payment_kind and getattr(payment_kind, 'requires_bank', False) and not bank:
            self.add_error('bank', _("This field is required for the selected payment kind."))

        return cleaned_data

class FruitPurchaseOrderReceiptForm(forms.ModelForm):
    class Meta:
        model = FruitPurchaseOrderReceipt
        fields = (
            'ooid',
            'fruit_purchase_order',
            'receipt_kind',
            'provider',
            'price_category',
            'container_capacity',
            'quantity',
            'unit_price',
            'total_cost',
            'balance_payable',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = self.instance

        self._can_edit_prices = True

        # Deshabilitar siempre total_cost y balance_payable
        for field in ['total_cost', 'balance_payable']:
            self.fields[field].disabled = True
            self.fields[field].widget.attrs['class'] = self.fields[field].widget.attrs.get('class', '') + ' readonly-field'

        # Si hay instancia, validamos los pagos
        if instance and instance.pk:
            payments = instance.fruitpurchaseorderpayment_set.all()
            has_payments = payments.exists()
            all_canceled = has_payments and all(p.status == 'canceled' for p in payments)
            any_active = any(p.status != 'canceled' for p in payments)

            if any_active:
                # Ningún campo editable
                for field in self.fields:
                    self.fields[field].disabled = True
                    self.fields[field].widget.attrs['class'] = self.fields[field].widget.attrs.get('class', '') + ' readonly-field'
                self._can_edit_prices = False
            elif all_canceled:
                # Solo quantity y unit_price editables
                for field in self.fields:
                    if field not in ['quantity', 'unit_price', 'total_cost', 'balance_payable']:
                        self.fields[field].disabled = True
                        self.fields[field].widget.attrs['class'] = self.fields[field].widget.attrs.get('class', '') + ' readonly-field'
                self._can_edit_prices = True


    def clean(self):
        cleaned_data = super().clean()

        if self._can_edit_prices:
            quantity = cleaned_data.get('quantity')
            unit_price = cleaned_data.get('unit_price')

            if quantity is not None and unit_price is not None:
                total_cost = (Decimal(quantity) * Decimal(unit_price)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                cleaned_data['total_cost'] = total_cost
                cleaned_data['balance_payable'] = total_cost  # Porque todos los pagos están cancelados

        return cleaned_data

class FruitOrderPaymentForm(forms.ModelForm):
    class Meta:
        model = FruitPurchaseOrderPayment
        fields = (
            'fruit_purchase_order_receipt',
            'payment_date',
            'payment_kind',
            'amount',
            'bank',
            'comments',
            'additional_inputs',
            'proof_of_payment',
        )
        widgets = {
            'additional_inputs': forms.HiddenInput(),
            'proof_of_payment': CustomFileDisplayWidget()
        }

    def __init__(self, *args, fruit_purchase_order=None, **kwargs):
        super().__init__(*args, **kwargs)

        fruit_order = fruit_purchase_order or getattr(self.instance, 'fruit_purchase_order', None)

        if fruit_order:
            self.fields['fruit_purchase_order_receipt'].queryset = FruitPurchaseOrderReceipt.objects.filter(
                fruit_purchase_order=fruit_order
            )
        else:
            self.fields['fruit_purchase_order_receipt'].queryset = FruitPurchaseOrderReceipt.objects.none()

        instance = self.instance
        if instance and instance.pk:
            for field in self.fields:
                self.fields[field].disabled = True
                self.fields[field].widget.attrs['class'] = self.fields[field].widget.attrs.get('class',
                                                                                               '') + ' readonly-field'

            if 'payment_date' in self.fields:
                self.fields['payment_date'].widget = forms.TextInput(attrs={
                    'readonly': 'readonly',
                    'class': 'readonly-field'
                })

            if instance.additional_inputs:
                self.fields['additional_inputs'].initial = json.dumps(instance.additional_inputs)

        for field_name in ['payment_kind', 'bank']:
            if hasattr(self.fields[field_name].widget, 'can_add_related'):
                self.fields[field_name].widget.can_add_related = False
                self.fields[field_name].widget.can_change_related = False
                self.fields[field_name].widget.can_delete_related = False
                self.fields[field_name].widget.can_view_related = False

        self.fields['bank'].required = False

    def clean(self):
        cleaned_data = super().clean()
        payment_kind = cleaned_data.get('payment_kind')
        bank = cleaned_data.get('bank')

        if payment_kind and getattr(payment_kind, 'requires_bank', False) and not bank:
            self.add_error('bank', _("This field is required for the selected payment kind."))

        receipt = cleaned_data.get('fruit_purchase_order_receipt')
        order = self.instance.fruit_purchase_order

        if receipt and receipt.fruit_purchase_order != order:
            self.add_error('fruit_purchase_order_receipt', _("This receipt does not belong to the selected order."))

        return cleaned_data

class FruitPaymentInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, fruit_purchase_order=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fruit_purchase_order = fruit_purchase_order

    def _construct_form(self, i, **kwargs):
        kwargs['fruit_purchase_order'] = self.fruit_purchase_order
        return super()._construct_form(i, **kwargs)


