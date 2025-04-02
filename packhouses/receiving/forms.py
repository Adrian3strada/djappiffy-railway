from django import forms
from django.utils.translation import gettext_lazy as _
from packhouses.gathering.models import ScheduleHarvestVehicle
from .models import IncomingProduct, PalletReceived
from django.core.exceptions import ValidationError

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

class IncomingProductForm(forms.ModelForm):
    class Meta:
        model = IncomingProduct
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()

        # obtener el status a guardar para validaciones
        incoming_product_status = cleaned_data.get('status', self.instance.status)

        # VALIDACIÓN DE PARA PALLETS RECEIVED
        total_pallets = int(self.data.get('palletreceived_set-TOTAL_FORMS', 0))

        if total_pallets < 1 and incoming_product_status != "pending":
            raise forms.ValidationError("You must add at least one Pallet to the Incoming Product.")

        for i in range(total_pallets):
            pallet_prefix = f'palletreceived_set-{i}-' 
            provider = self.data.get(pallet_prefix + 'provider')
            harvesting_crew = self.data.get(pallet_prefix + 'harvesting_crew')

            if not provider or not provider.strip():
                raise ValidationError(_(f'Pallet Received {i + 1} is missing a provider.'))

            if not harvesting_crew or not harvesting_crew.strip():
                raise ValidationError(_(f'Pallet Received {i + 1} is missing a harvesting crew.'))

        return cleaned_data
