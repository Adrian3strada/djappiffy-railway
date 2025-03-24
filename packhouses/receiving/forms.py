from django import forms
from django.utils.translation import gettext_lazy as _
from packhouses.gathering.models import ScheduleHarvestVehicle

class ScheduleHarvestVehicleForm(forms.ModelForm):
    stamp_vehicle_number = forms.CharField(label=_('Stamp'), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.initial_incoming_status = None
        if self.instance and self.instance.pk:
            try:
                self.initial_incoming_status = self.instance.harvest_cutting.incoming_product.status
            except Exception:
                pass  
            
        if self.initial_incoming_status != 'pending':
            self.fields['stamp_vehicle_number'].required = False
            if self.instance and self.instance.pk:
                self.fields['stamp_vehicle_number'].initial = self.instance.stamp_number

    def clean(self):
        cleaned_data = super().clean()
        input_stamp = cleaned_data.get('stamp_vehicle_number')

        try:
            new_incoming_status = self.cleaned_data['harvest_cutting'].incoming_product.status
        except Exception:
            new_incoming_status = None

        if self.initial_incoming_status == 'pending' and new_incoming_status != 'pending':
            if not input_stamp:
                raise forms.ValidationError(_("You must enter the stamp number."))

            harvest_cutting = cleaned_data.get('harvest_cutting')
            vehicle = cleaned_data.get('vehicle')

            if not harvest_cutting or not vehicle:
                raise forms.ValidationError(_("The stamp cannot be validated: missing data."))

            # Validar coincidencia del sello
            expected_vehicle = ScheduleHarvestVehicle.objects.filter(
                harvest_cutting=harvest_cutting,
                vehicle=vehicle
            ).first()


            if not expected_vehicle or expected_vehicle.stamp_number != input_stamp:
                raise forms.ValidationError(_("Invalid stamp number."))

        return cleaned_data

    class Meta:
        model = ScheduleHarvestVehicle
        fields = "__all__"