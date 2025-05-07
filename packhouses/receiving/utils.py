from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.forms.models import BaseInlineFormSet

def update_weighing_set_numbers(incoming_product):
    pallets = incoming_product.weighingset_set.all().order_by('id')
    with transaction.atomic():
        for index, pallet in enumerate(pallets, start=1):
            if pallet.ooid != index:
                pallet.ooid = index
                pallet.save(update_fields=['ooid'])

def get_approval_status_choices():
    return [
        ('pending',    _('Pending')),
        ('accepted',   _('Accepted')),
        ('rejected',   _('Rejected')),
        ('quarantine', _('Quarantine')),
    ]


def get_processing_status_choices():
    return [
        ('pending', _('Pending')),
        ('in_operation', 'In Operation'),
        ('in_another_batch', 'In Another Batch'),
        ('canceled', 'Canceled'),
        ('finalized', 'Finalized'),
]

def get_batch_status_change (): 
    return [
        ('operational_status', 'Operational Status'),
        ('review_status',      'Review Status'),
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