from django import forms
from django.utils.translation import gettext_lazy as _
from packhouses.gathering.models import ScheduleHarvestVehicle

class ScheduleHarvestVehicleForm(forms.ModelForm):
    stamp_vehicle_number = forms.CharField(label=_('Stamp'), required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self.instance and self.instance.pk:
            try:
                self.incoming_status = self.instance.harvest_cutting.incoming_product.status
            except Exception:
                self.incoming_status = None

            if self.incoming_status and self.incoming_status != 'pending':
                self.fields['stamp_vehicle_number'].initial = self.instance.stamp_number

    def clean(self):
        cleaned_data = super().clean()
        input_stamp = cleaned_data.get('stamp_vehicle_number')

        incoming_status = getattr(self, 'incoming_status', None)
        print(incoming_status)
        if incoming_status == 'pending':
            return cleaned_data  

        if not input_stamp:
            raise forms.ValidationError(_("You must enter the stamp number."))

        harvest_cutting = cleaned_data.get('harvest_cutting') or getattr(self.instance, 'harvest_cutting', None)
        vehicle = cleaned_data.get('vehicle') or getattr(self.instance, 'vehicle', None)

        if not harvest_cutting or not vehicle:
            raise forms.ValidationError(_("The stamp cannot be validated: missing harvest or vehicle data."))

        vehicles_same_cut = ScheduleHarvestVehicle.objects.filter(harvest_cutting=harvest_cutting)
        
        expected_vehicle = vehicles_same_cut.filter(vehicle=vehicle).first()

        if not expected_vehicle:
            raise forms.ValidationError(_("The stamp cannot be validated: missing cut or vehicle data."))

        if expected_vehicle.stamp_number != input_stamp:
            raise forms.ValidationError(
                _("The entered stamp number ({entered}) does not match the expected one ({expected}).")
                .format(entered=input_stamp, expected=expected_vehicle.stamp_number)
            )

        return cleaned_data

    class Meta:
        model = ScheduleHarvestVehicle
        fields = "__all__"