from django import forms
from .models import WorkShiftSchedule, EmployeeContactInformation
from cities_light.models import City, Country, Region, SubRegion
class WorkShiftScheduleForm(forms.ModelForm):
    # Campo "day" oculto para nuevos registros
    day = forms.CharField(widget=forms.HiddenInput(), required=True)

    class Meta:
        model = WorkShiftSchedule
        fields = ('day', 'entry_time', 'exit_time', 'is_enabled')

class EmployeeContactInformationForm(forms.ModelForm):
    class Meta:
        model = EmployeeContactInformation
        fields = [
            'country', 'state', 'city', 'district',
            'postal_code', 'neighborhood', 'address',
            'phone_number', 'email', 'employee'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Inicializar vacíos por defecto
        self.fields['state'].queryset = Region.objects.none()
        self.fields['city'].queryset = SubRegion.objects.none()
        self.fields['district'].queryset = City.objects.none()

        if self.is_bound:
            country_id = self.data.get(self.add_prefix('country'))
            state_id = self.data.get(self.add_prefix('state'))
            city_id = self.data.get(self.add_prefix('city'))

            if country_id:
                self.fields['state'].queryset = Region.objects.filter(country_id=country_id)
            if state_id:
                self.fields['city'].queryset = SubRegion.objects.filter(region_id=state_id)
            if city_id:
                self.fields['district'].queryset = City.objects.filter(subregion_id=city_id)

        elif self.instance.pk:
            if self.instance.country:
                self.fields['state'].queryset = Region.objects.filter(country=self.instance.country)
            if self.instance.state:
                self.fields['city'].queryset = SubRegion.objects.filter(region=self.instance.state)
            if self.instance.city:
                self.fields['district'].queryset = City.objects.filter(subregion=self.instance.city)
