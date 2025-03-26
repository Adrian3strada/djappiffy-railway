from django.utils.translation import gettext_lazy as _
from django.db import transaction

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
