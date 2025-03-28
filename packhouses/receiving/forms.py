from django import forms
from django.utils.translation import gettext_lazy as _
from packhouses.gathering.models import ScheduleHarvestVehicle
from .models import IncomingProduct

class ScheduleHarvestVehicleForm(forms.ModelForm):
    stamp_vehicle_number = forms.CharField(
        label=_('Stamp'),
        required=False,  # Inicialmente no obligatorio, pero lo validaremos manualmente
    )

    class Meta:
        model = ScheduleHarvestVehicle
        fields = ['stamp_vehicle_number', 'vehicle', 'provider', 'harvest_cutting']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Obtener el estado inicial del vehículo
        if self.instance and self.instance.pk:
            try:
                self.initial_incoming_status = self.instance.harvest_cutting.incoming_product.status
                print(f"Estado inicial del vehículo con ID {self.instance.id}: {self.initial_incoming_status}")
            except Exception as e:
                print(f"Error al obtener el estado inicial del vehículo: {str(e)}")
                self.initial_incoming_status = None
        else:
            self.initial_incoming_status = None
            print("No hay vehículo asociado a este formulario o no se ha encontrado el ID.")
        
        if self.initial_incoming_status == 'pending':
            # Si el estado inicial es 'pending', el sello será obligatorio
            self.fields['stamp_vehicle_number'].required = True
            self.fields['stamp_vehicle_number'].initial = ''  # Dejar vacío el campo para que no se marque como vacío
            print("El estado es 'pending', el sello es obligatorio.")
        else:
            # Si el estado no es 'pending', se autorrellena con el sello guardado
            self.fields['stamp_vehicle_number'].required = False
            self.fields['stamp_vehicle_number'].initial = self.instance.stamp_number if self.instance else ''
            print(f"El estado no es 'pending'. El sello se pre-llenará con: {self.fields['stamp_vehicle_number'].initial}")
    
    def clean_stamp_vehicle_number(self):
        stamp_number = self.cleaned_data.get('stamp_vehicle_number')
        print(f"Sello ingresado en el formulario: {stamp_number}")

        # Si el estado es 'pending', siempre validamos el sello
        if self.initial_incoming_status == 'pending':
            # Validamos que el sello ingresado coincida con el guardado en el modelo
            if self.instance and self.instance.stamp_number != stamp_number:
                print(f"El sello ingresado {stamp_number} no coincide con el sello guardado {self.instance.stamp_number}")
                raise forms.ValidationError(_('El sello ingresado no coincide con el sello guardado.'))
            else:
                print(f"Sello ingresado {stamp_number} coincide con el sello guardado.")
        
        return stamp_number
