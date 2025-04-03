from django import forms
from django.utils.translation import gettext_lazy as _
from packhouses.gathering.models import ScheduleHarvestVehicle
from .models import IncomingProduct, PalletReceived
from django.core.exceptions import ValidationError


class ScheduleHarvestVehicleForm(forms.ModelForm):
    stamp_vehicle_number = forms.CharField(
        label=_('Stamp'),
        required=False,
    )

    class Meta:
        model = ScheduleHarvestVehicle
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        
        # Obtener estado inicial desde la instancia relacionada
        initial_status = None
        if self.instance.pk:
            schedule_harvest = self.instance.harvest_cutting
            if schedule_harvest and schedule_harvest.incoming_product:
                initial_status = schedule_harvest.incoming_product.status
                print("INICIO", initial_status)
        
        # Obtener estado final desde el POST
        final_status = self.data.get('status')
        print("FINAL", final_status)
        
        # Ejemplo de validación: Requerir stamp si el estado cambia
        if initial_status != final_status:
            stamp = cleaned_data.get('stamp_vehicle_number')
            if not stamp:
                self.add_error('stamp_vehicle_number', 'Este campo es obligatorio cuando cambia el estado.')
        
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

        # VALIDACIÓN PARA PALLETS RECEIVED:
        total_pallets = int(self.data.get('palletreceived_set-TOTAL_FORMS', 0))
        if total_pallets < 1 and final_status != "pending":
            raise ValidationError("You must add at least one Pallet to the Incoming Product.")

        for i in range(total_pallets):
            pallet_prefix = f'palletreceived_set-{i}-'
            provider = self.data.get(pallet_prefix + 'provider')
            harvesting_crew = self.data.get(pallet_prefix + 'harvesting_crew')

            if not provider or not provider.strip():
                raise ValidationError(_(f'Pallet Received {i + 1} is missing a provider.'))
            if not harvesting_crew or not harvesting_crew.strip():
                raise ValidationError(_(f'Pallet Received {i + 1} is missing a harvesting crew.'))

        return cleaned_data
