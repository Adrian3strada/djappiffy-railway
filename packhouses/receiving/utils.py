from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.forms.models import BaseInlineFormSet

def update_pallet_numbers(incoming_product):
    pallets = incoming_product.palletreceived_set.all().order_by('id')
    with transaction.atomic():
        for index, pallet in enumerate(pallets, start=1):
            if pallet.ooid != index:
                pallet.ooid = index
                pallet.save(update_fields=['ooid'])

def get_incoming_product_categories_status():
    return [
        ('pending', _('Pending')),
        ('accepted', _('Accepted')),
        ('rejected', _('Rejected')),
        ('quarintine', _('Quarintine')),
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