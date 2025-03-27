from django import forms
from django.utils.translation import gettext_lazy as _
from packhouses.gathering.models import ScheduleHarvestVehicle
from .models import IncomingProduct

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
            
        if self.initial_incoming_status == 'pending':
            self.fields['stamp_vehicle_number'].initial = ''
        else:
            self.fields['stamp_vehicle_number'].initial = self.instance.stamp_number if self.instance else ''
            self.fields['stamp_vehicle_number'].required = False
            
    class Meta:
        model = ScheduleHarvestVehicle
        fields = "__all__"
