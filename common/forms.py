from django import forms
from django.forms.models import ModelChoiceIteratorValue

class SelectWidgetWithAlias(forms.Select):
    def __init__(self, model, alias_field, *args, **kwargs):
        self.model = model
        self.alias_field = alias_field
        self._alias_cache = {}
        super().__init__(*args, **kwargs)

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        if isinstance(value, ModelChoiceIteratorValue):
            value = value.value
        if value:
            if value not in self._alias_cache:
                try:
                    instance = self.model.objects.get(pk=value)
                    alias_value = getattr(instance, self.alias_field)
                    self._alias_cache[value] = alias_value
                except self.model.DoesNotExist:
                    self._alias_cache[value] = None
            option['attrs']['data-alias'] = self._alias_cache.get(value, '')
        return option
