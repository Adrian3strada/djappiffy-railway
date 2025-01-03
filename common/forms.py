from django import forms
from django.forms.models import ModelChoiceIteratorValue

class SelectWidgetWithData(forms.Select):
    def __init__(self, model, data_field, *args, **kwargs):
        self.model = model
        self.data_field = data_field
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
                    data_value = getattr(instance, self.data_field)
                    self._data_cache[value] = data_value
                except self.model.DoesNotExist:
                    self._data_cache[value] = None

            option['attrs'][f'data-{self.data_field}'] = str(self._data_cache.get(value, ''))

        return option
