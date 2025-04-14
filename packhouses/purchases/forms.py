from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Requisition, PurchaseOrder, PurchaseOrderPayment
from django.forms.models import ModelChoiceField
import json
from django.utils.safestring import mark_safe



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
        if self.instance and self.instance.pk:
            for field in self.fields:
                self.fields[field].disabled = True
                # Agregar clase readonly-field a todos los campos deshabilitados
                if 'class' in self.fields[field].widget.attrs:
                    self.fields[field].widget.attrs['class'] += ' readonly-field'
                else:
                    self.fields[field].widget.attrs['class'] = 'readonly-field'

            self.fields['payment_date'].widget = forms.TextInput(attrs={
                'readonly': 'readonly',
                'class': 'readonly-field'
            })

            # Si hay datos en additional_inputs, asignar el JSON al campo
            if self.instance.additional_inputs:
                self.fields['additional_inputs'].initial = json.dumps(self.instance.additional_inputs)

        # Agregar clase readonly-field a cualquier campo que sea readonly o disabled
        for field_name, field in self.fields.items():
            if field.disabled or field.widget.attrs.get('readonly', False):
                if 'class' in field.widget.attrs:
                    if 'readonly-field' not in field.widget.attrs['class']:
                        field.widget.attrs['class'] += ' readonly-field'
                else:
                    field.widget.attrs['class'] = 'readonly-field'

        for field_name in ['payment_kind', 'bank']:
            if hasattr(self.fields[field_name].widget, 'can_add_related'):
                self.fields[field_name].widget.can_add_related = False
                self.fields[field_name].widget.can_change_related = False
                self.fields[field_name].widget.can_delete_related = False
                self.fields[field_name].widget.can_view_related = False

