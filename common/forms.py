from django import forms
from django.forms.models import ModelChoiceIteratorValue

class SelectWidgetWithData(forms.Select):
    def __init__(self, model, data_fields, *args, **kwargs):
        self.model = model
        self.data_fields = data_fields if isinstance(data_fields, list) else [data_fields]
        self._data_cache = {}
        super().__init__(*args, **kwargs)

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)

        if isinstance(value, ModelChoiceIteratorValue):
            value = value.value

        if value:
            if value not in self._data_cache:
                try:
                    instance = self.model.objects.get(pk=value)
                    self._data_cache[value] = {
                        field: getattr(instance, field, '') for field in self.data_fields
                    }
                except self.model.DoesNotExist:
                    self._data_cache[value] = {field: '' for field in self.data_fields}

            # Agregar múltiples atributos de datos
            for field in self.data_fields:
                option['attrs'][f'data-{field}'] = str(self._data_cache[value].get(field, ''))

        return option
