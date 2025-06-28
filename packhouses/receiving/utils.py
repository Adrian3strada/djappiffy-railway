from django.utils.translation import gettext_lazy as _, gettext
from django.db import transaction
from django.forms.models import BaseInlineFormSet
from django.apps import apps
from common.settings import STATUS_CHOICES


def update_weighing_set_numbers(incoming_product):
    pallets = incoming_product.weighingset_set.all().order_by('id')
    with transaction.atomic():
        for index, pallet in enumerate(pallets, start=1):
            if pallet.ooid != index:
                pallet.ooid = index
                pallet.save(update_fields=['ooid'])


def get_processing_status_choices():
    return [
        ('pending', _('Pending')),
        ('in_operation', 'In Operation'),
        ('in_another_batch', 'In Another Batch'),
        ('canceled', 'Canceled'),
        ('finalized', 'Finalized'),
    ]


def get_batch_status_change():
    return [
        ('operational_status', 'Operational Status'),
        ('review_status', 'Review Status'),
    ]


class CustomScheduleHarvestFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.forms:
            if 'product_provider' in form.fields:
                form.fields['product_provider'].widget.can_add_related = False
                form.fields['product_provider'].widget.can_change_related = False
                form.fields['product_provider'].widget.can_delete_related = False
                form.fields['product_provider'].widget.can_view_related = False
            if 'product' in form.fields:
                form.fields['product'].widget.can_add_related = False
                form.fields['product'].widget.can_change_related = False
                form.fields['product'].widget.can_delete_related = False
                form.fields['product'].widget.can_view_related = False
            if 'maquiladora' in form.fields:
                form.fields['maquiladora'].widget.can_add_related = False
                form.fields['maquiladora'].widget.can_change_related = False
                form.fields['maquiladora'].widget.can_delete_related = False
                form.fields['maquiladora'].widget.can_view_related = False
            if 'gatherer' in form.fields:
                form.fields['gatherer'].widget.can_add_related = False
                form.fields['gatherer'].widget.can_change_related = False
                form.fields['gatherer'].widget.can_delete_related = False
                form.fields['gatherer'].widget.can_view_related = False
            if 'orchard' in form.fields:
                form.fields['orchard'].widget.can_add_related = False
                form.fields['orchard'].widget.can_change_related = False
                form.fields['orchard'].widget.can_delete_related = False
                form.fields['orchard'].widget.can_view_related = False
            if 'market' in form.fields:
                form.fields['market'].widget.can_add_related = False
                form.fields['market'].widget.can_change_related = False
                form.fields['market'].widget.can_delete_related = False
                form.fields['market'].widget.can_view_related = False
            if 'weighing_scale' in form.fields:
                form.fields['weighing_scale'].widget.can_add_related = False
                form.fields['weighing_scale'].widget.can_change_related = False
                form.fields['weighing_scale'].widget.can_delete_related = False
                form.fields['weighing_scale'].widget.can_view_related = False


FILTER_DISPLAY_CONFIG = {
    'Batch': {
        'ordering': [
            'incomingproduct__scheduleharvest__orchard__producer',
            'incomingproduct__scheduleharvest__gatherer',
            'incomingproduct__scheduleharvest__maquiladora',
            'incomingproduct__scheduleharvest__product_provider',
            'incomingproduct__scheduleharvest__harvesting_crew',
            'orchard_certification',
            'incomingproduct__scheduleharvest__orchard__category',
            'incomingproduct__scheduleharvest__product',
            'incomingproduct__scheduleharvest__product_phenology',
            'scheduleharvest_is_scheduled',
            'incomingproduct__scheduleharvest__category',
            'is_available_for_processing',
            'batch_type',
            'status',
        ],
        'renames': {
            'incomingproduct__scheduleharvest__orchard__producer': _('Producer'),
            'incomingproduct__scheduleharvest__gatherer': _('Gatherer'),
            'incomingproduct__scheduleharvest__maquiladora': _('Maquiladora'),
            'incomingproduct__scheduleharvest__product_provider': _('Product Provider'),
            'incomingproduct__scheduleharvest__harvesting_crew': _('Harvesting Crew'),
            'orchard_certification': _('Orchard Certification'),
            'incomingproduct__scheduleharvest__orchard_product_category': _('Product Category'),
            'incomingproduct__scheduleharvest__product': _('Product'),
            'incomingproduct__scheduleharvest__product_phenology': _('Product Phenology'),
            'scheduleharvest_is_scheduled': _('Scheduling Type'),
            'incomingproduct__scheduleharvest__category': _('Harvesting Category'),
            'is_available_for_processing': _('Available for Processing'),
            'batch_type': _('Batch Type'),
            'status': _('Status'),
        },
        'transform': {
            'scheduleharvest_is_scheduled': lambda val: _('Scheduled') if val == '1' else _('Unscheduled'),
            'is_available_for_processing': lambda val: _('Yes') if val == '1' else _('No'),
            'batch_type': lambda val: {
                'independent': _('Independent Batch'),
                'parent': _('Parent Batch'),
                'child': _('Child Batch'),
            }.get(val, val),
            'status': lambda val: dict(STATUS_CHOICES).get(val, val),
        }
    },
    'IncomingProduct': {
        'ordering': [
            'orchard__producer',
            'gatherer',
            'maquiladora',
            'product_provider',
            'harvesting_crew',
            'orchard_certification'
            'orchard_product_category',
            'product',
            'product_phenology',
            'is_scheduled',
            'category',
            'status',
        ],
        'renames': {
            'product': _('Product'),
            'product_phenology': _('Product Phenology'),
            'category': _('Harvesting Category'),
            'maquiladora': _('Maquiladora'),
            'gatherer': _('Gatherer'),
            'status': _('Status'),
            'product_provider': _('Product Provider'),
            'category_sh': _('Harvesting Category'),
            'harvesting_crew': _('Harvesting Crew'),
            'orchard_product_category': _('Product Category'),
            'is_scheduled': _('Scheduling Type'),
        },
        'transform': {
            'is_scheduled': lambda val: _('Scheduled') if val == '1' else _('Unscheduled')
        }
    }
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

    ordering = config['ordering']
    renames = config['renames']
    transforms = config['transform']

    BatchModel = apps.get_model("receiving", "Batch")
    IncomingProductModel = apps.get_model("receiving", "IncomingProduct")
    ScheduleHarvestModel = apps.get_model("gathering", "ScheduleHarvest")

    internal_map = {}

    for key, val in applied_filters.items():
        normalized_key = key
        related_model = None

        if model_key == 'IncomingProduct':
            if key.startswith('scheduleharvest__') or key.startswith('scheduleharvest_'):
                normalized_key = key.split('__', 1)[-1] if '__' in key else key[len('scheduleharvest_'):]
                related_model = ScheduleHarvestModel
            else:
                normalized_key = key
                related_model = IncomingProductModel

        elif model_key == 'Batch':
            if key.startswith("incomingproduct__scheduleharvest__"):
                normalized_key = key
                related_model = ScheduleHarvestModel
            elif key.startswith("incomingproduct__"):
                normalized_key = key
                related_model = IncomingProductModel
            elif key in ['status', 'is_available_for_processing']:
                normalized_key = key
                related_model = BatchModel
            else:
                normalized_key = key
                related_model = None

        if normalized_key in transforms:
            try:
                val = transforms[normalized_key](val)
            except Exception:
                pass

        if related_model:
            try:
                field_path = normalized_key.split('__')[-1]
                field_obj = related_model._meta.get_field(field_path)
                raw_val = field_obj.to_python(val)

                if field_obj.choices:
                    val = gettext(dict(field_obj.choices).get(raw_val, raw_val))
                elif hasattr(field_obj, 'remote_field') and field_obj.remote_field:
                    instance = field_obj.remote_field.model.objects.filter(pk=raw_val).first()
                    val = str(instance) if instance else raw_val
                else:
                    val = raw_val
            except Exception:
                pass

        label = renames.get(normalized_key, normalized_key.replace('_', ' ').title())
        internal_map[normalized_key] = (label, val)

    ordered = {}
    for key_in_order in ordering:
        if key_in_order in internal_map:
            label, value = internal_map.pop(key_in_order)
            ordered[label] = value
    for label, value in internal_map.values():
        ordered[label] = value

    return ordered
