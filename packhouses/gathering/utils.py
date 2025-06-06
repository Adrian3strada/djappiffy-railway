from django.utils.translation import gettext_lazy as _, gettext
from .models import ScheduleHarvest 

FILTER_DISPLAY_CONFIG = {
    'ScheduleHarvest': {
        'ordering': [
            'orchard_certification',
            'scheduleharvest_product_producer',
            'gatherer',
            'maquiladora',
            'scheduleharvest_product_provider',
            'harvesting_crew',
            'orchard_certification',
            'orchard_product_category',
            'product',
            'product_phenology',
            'is_scheduled',
            'category',
            'status',
        ],
        'renames': {
            'scheduleharvest_product_producer': _('Product Provider'),
            'scheduleharvest_product_provider': _('Product Producer'),
            'harvesting_crew': _('Harvesting Crew'),
            'product': _('Product'),
            'product_phenology': _('Product Phenology'),
            'orchard_product_category': _('Product Category'),
            'orchard_certification': _('Orchard Certification'),
            'category': _('Harvesting Category'),
            'maquiladora': _('Maquiladora'),
            'gatherer': _('Gatherer'),
            'is_scheduled': _('Scheduling Type'),
            'status': _('Status'),
        },
        'transform': {
            'is_scheduled': lambda val: _('Scheduled') if val == '1' else _('Unscheduled')
        }
    },
}


def get_filter_config(model_key):
    raw_config = FILTER_DISPLAY_CONFIG.get(model_key)

    if not raw_config:
        return {}

    renames = {k: str(gettext(v)) for k, v in raw_config.get('renames', {}).items()}

    return {
        'ordering': raw_config.get('ordering', []),
        'renames': renames,
        'transform': raw_config.get('transform', {}),
    }

def apply_filter_config(applied_filters, model_key):
    config = get_filter_config(model_key)
    if not config:
        return applied_filters

    ordering  = config['ordering']
    renames   = config['renames']
    transforms = config['transform']

    Model = ScheduleHarvest
    internal_map = {}

    for key, val in applied_filters.items():
        if key in transforms:
            try:
                val = transforms[key](val)
            except Exception:
                pass

        if key.endswith('__range'):
            field_name = key.replace('__range', '')
            try:
                field_obj = Model._meta.get_field(field_name)
                etiqueta = str(gettext(field_obj.verbose_name)).title()
            except Exception:
                etiqueta = renames.get(key, key.replace('_', ' ').title())
        else:
            etiqueta = renames.get(key, key.replace('_', ' ').title())

        internal_map[key] = (etiqueta, val)

    ordered = {}
    for key_in_order in ordering:
        if key_in_order in internal_map:
            label, value = internal_map.pop(key_in_order)
            ordered[label] = value

    for label, value in internal_map.values():
        ordered[label] = value

    return ordered
