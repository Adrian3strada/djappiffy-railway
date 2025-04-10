from django import forms
from django.utils.translation import gettext_lazy as _
from packhouses.gathering.models import ScheduleHarvestVehicle
from .models import IncomingProduct
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from django.utils.safestring import mark_safe

class BaseScheduleHarvestVehicleFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        incoming_status = None
        if hasattr(self.instance, 'incoming_product'):
            incoming_status = self.instance.incoming_product.status
        else:
            incoming_status = self.data.get('status')

        if incoming_status == "accepted":
            valid_forms = [
                form.cleaned_data
                for form in self.forms
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False)
            ]
            
            has_arrived_flags = [data.get('has_arrived', False) for data in valid_forms]
            
            if not any(has_arrived_flags):
                error_msg = mark_safe('<span style="color: red;">You must register at least one vehicle as having arrived for the Incoming Product.</span>')
                raise ValidationError(error_msg)
        

class ScheduleHarvestVehicleForm(forms.ModelForm):
    stamp_vehicle_number = forms.CharField(label=_('Stamp'), required=True,)

    class Meta:
        model = ScheduleHarvestVehicle
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        has_arrived_init = self.instance.has_arrived
        if has_arrived_init:
            self.fields['stamp_vehicle_number'].initial = self.instance.stamp_number
        else:
            self.fields['stamp_vehicle_number'].initial = ""

        if request:
            if request.POST:
                has_arrived_str = request.POST.get('has_arrived')
                has_arrived = has_arrived_str == 'on'
                self.fields['stamp_vehicle_number'].required = has_arrived
            else:
                self.fields['stamp_vehicle_number'].required = True

    def clean(self):
        cleaned_data = super().clean()
        stamp_vehicle_number = cleaned_data.get('stamp_vehicle_number')
        guide_number = cleaned_data.get('guide_number') 

        instance = self.instance
        has_arrived_initial = instance.has_arrived if instance and instance.pk else False
        has_arrived_final = cleaned_data.get('has_arrived', has_arrived_initial)

        errors = {} 
        # Validación cuando cambia de False → True
        if not has_arrived_initial and has_arrived_final:
            if stamp_vehicle_number and instance and instance.stamp_number != stamp_vehicle_number:
                errors['stamp_vehicle_number'] = _('The provided Stamp does not match the original.')
            
            if not stamp_vehicle_number:
                self.fields['stamp_vehicle_number'].required = True
                errors['stamp_vehicle_number'] = _('Stamp Vehicle Number is required when the vehicle has arrived.')

            if not guide_number:
                self.fields['guide_number'].required = True
                errors['guide_number'] = _('Guide Number is required when the vehicle has arrived.')
        if errors:
            raise forms.ValidationError(errors)

        return cleaned_data


class IncomingProductForm(forms.ModelForm):
    class Meta:
        model = IncomingProduct
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()

        # Status guardado en la base de datos
        initial_status = self.instance.status if self.instance and self.instance.pk else None
        # Obtiener el status final
        final_status = cleaned_data.get('status', initial_status)

        # VALIDACIÓN PARA PESADAS:
        total_weighing_sets = int(self.data.get('weighingset_set-TOTAL_FORMS', 0))

        remaining_weighing_sets = 0
        for i in range(total_weighing_sets):
            delete_key = f'weighingset_set-{i}-DELETE'
            if self.data.get(delete_key, 'off') != 'on':
                remaining_weighing_sets += 1

        if remaining_weighing_sets < 1 and final_status == "accepted":
            raise ValidationError("At least one Weighing Set must be registered for the Incoming Product.")

        for i in range(remaining_weighing_sets):
            weighingset_prefix = f'weighingset_set-{i}-'
            provider = self.data.get(weighingset_prefix + 'provider')
            harvesting_crew = self.data.get(weighingset_prefix + 'harvesting_crew')

            if not provider or not provider.strip():
                raise ValidationError(_(f'Weighing Set {i + 1} is missing a provider.'))
            if not harvesting_crew or not harvesting_crew.strip():
                raise ValidationError(_(f'Weighing Set {i + 1} is missing a harvesting crew.'))
        

        return cleaned_data
