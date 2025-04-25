from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Requisition, PurchaseOrder, PurchaseOrderPayment,RequisitionSupply
from django.forms.models import ModelChoiceField
import json
from django.utils.safestring import mark_safe
from packhouses.catalogs.models import Supply
from django.db import models


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
        purchase_order_supplies = self.data.getlist('purchaseordersupply_set-TOTAL_FORMS', [])
        if not purchase_order_supplies or int(purchase_order_supplies[0]) < 1:
            raise ValidationError(_("You must add at least one supply to the purchases order."))

        return cleaned_data


class PurchaseOrderPaymentForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderPayment
        fields = ('payment_date', 'payment_kind', 'amount', 'bank', 'comments', 'additional_inputs')
        widgets = {
            'additional_inputs': forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        instance = self.instance

        # Si está en modo lectura
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

        # Quitar controles relacionados para evitar botones "Agregar nuevo"
        for field_name in ['payment_kind', 'bank']:
            if hasattr(self.fields[field_name].widget, 'can_add_related'):
                self.fields[field_name].widget.can_add_related = False
                self.fields[field_name].widget.can_change_related = False
                self.fields[field_name].widget.can_delete_related = False
                self.fields[field_name].widget.can_view_related = False

        # Marcamos el campo bank como no requerido de entrada
        self.fields['bank'].required = False

    def clean(self):
        cleaned_data = super().clean()
        payment_kind = cleaned_data.get('payment_kind')
        bank = cleaned_data.get('bank')

        if payment_kind and payment_kind.requires_bank and not bank:
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


