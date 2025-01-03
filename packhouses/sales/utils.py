from django.utils.translation import gettext_lazy as _

def incoterms_choices():
    return [
        ('EXW', 'EXW -- Ex Works'),
        ('FCA', 'FCA -- Free Carrier'),
        ('FAS', 'FAS -- Free Alongside Ship'),
        ('FOB', 'FOB -- Free on Board'),
        ('CFR', 'CFR -- Cost and Freight'),
        ('CIF', 'CIF -- Cost, Insurance & Freight'),
        ('CPT', 'CPT -- Carriage Paid To'),
        ('CIP', 'CIP -- Cost, Insurance & Freight'),
        ('DAP', 'DAP -- Delivered at Place'),
        ('DPU', 'DPU -- Delivered at Place Unloaded'),
        ('DDP', 'DDP -- Delivered Duty Paid'),
    ]

def order_status_choices():
    return [
        ('opened', _('Opened')),
        ('closed', _('Closed')),
        ('canceled', _('Canceled')),
    ]

def local_delivery_choices():
    return [
        ('plant', _('Delivery at Plant')),
        ('plant_transport', _('Delivery at Plant with Transportation Service')),
        ('warehouse', _('Delivery at Warehouse')),
        ('border', _('Delivery at Border')),
        ('consignee', _('Delivery to Consignee')),
    ]
