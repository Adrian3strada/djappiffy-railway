from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import ScheduleHarvest


class ScheduleHarvestForm(forms.ModelForm):
    class Meta:
        model = ScheduleHarvest
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()

        #INICIO DE VALIDACIONES PARA HARVESTING CREW

        # Obtener la cantidad de formularios del inline de HarvestingCrew
        total_forms_crews = int(self.data.get('scheduleharvestharvestingcrew_set-TOTAL_FORMS', 0))

        # Verificar que hay al menos un formulario agregado
        if total_forms_crews < 1:
            raise ValidationError(_("You must add at least one Harvesting Crew to the Schedule Harvest."))

        # Validar que los campos obligatorios de cada harvesting crew no estén vacíos
        for i in range(total_forms_crews):
            crew_prefix = f'scheduleharvestharvestingcrew_set-{i}-'  # Prefijo de cada form inline
            provider = self.data.get(crew_prefix + 'provider')
            harvesting_crew = self.data.get(crew_prefix + 'harvesting_crew')

            if not provider or not provider.strip():
                raise ValidationError(_(f'Harvesting Crew {i + 1} is missing a provider.'))

            if not harvesting_crew or not harvesting_crew.strip():
                raise ValidationError(_(f'Harvesting Crew {i + 1} is missing a harvesting_crew.'))

        #FIN DE VALIDACIONES PARA HARVESTING CREW

        #INICIO DE VALIDACIONES PARA VEHICLES

        # Obtener la cantidad de formularios del inline de ScheduleHarvestVehicle
        total_forms_vehicles = int(self.data.get('scheduleharvestvehicle_set-TOTAL_FORMS', 0))

        # Verificar que hay al menos un formulario agregado
        if total_forms_vehicles < 1:
            raise ValidationError(_("You must add at least one Vehicle to the Schedule Harvest."))

        # Validar que los campos obligatorios de cada vehicle no estén vacíos
        for i in range(total_forms_vehicles):
            vehicle_prefix = f'scheduleharvestvehicle_set-{i}-'
            provider = self.data.get(vehicle_prefix + 'provider')
            vehicle = self.data.get(vehicle_prefix + 'vehicle')
            stamp_number = self.data.get(vehicle_prefix + 'stamp_number')

            if not provider or not provider.strip():
                raise ValidationError(_(f'Vehicle {i + 1} is missing a provider.'))

            if not vehicle or not vehicle.strip():
                raise ValidationError(_(f'Vehicle {i + 1} is missing a vehicle.'))

            if not stamp_number or not stamp_number.strip():
                raise ValidationError(_(f'Vehicle {i + 1} is missing a stamp number.'))

        #FIN DE VALIDACIONES PARA VEHICLES

        return cleaned_data
