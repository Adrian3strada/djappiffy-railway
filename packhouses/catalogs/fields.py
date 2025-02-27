from django.db import models
from django.core.exceptions import ValidationError

class SupplyCapacityField(models.FloatField):
    def __init__(self, *args, **kwargs):
        self.kind_field = kwargs.pop('kind_field')
        super().__init__(*args, **kwargs)

    def clean(self, value, model_instance):
        kind = getattr(model_instance, self.kind_field)
        if kind.category in ['packaging_containment', 'packaging_separator', 'packaging_presentation',
                             'packaging_pallet', 'packaging_storage', 'packhouse_cleaning', 'packhouse_fuel']:
            if value < 0.01:
                raise ValidationError(
                    _('Capacity must be at least 0.01 for this kind.'),
                    params={'value': value},
                )
        else:
            if value != 0:
                raise ValidationError(
                    _('Capacity cannot be different than zero.'),
                    params={'value': value},
                )
        return super().clean(value, model_instance)
