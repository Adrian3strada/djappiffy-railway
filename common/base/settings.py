from django.utils.translation import gettext_lazy as _

SUPPLY_MEASURE_UNIT_CATEGORY_CHOICES = [
    ('pieces', _('Pieces')),
    ('g', _('grams')),
    ('Kg', _('Kilograms')),
    ('Ton', _('Tons')),
    ('ml', _('milliliters')),
    ('L', _('Liters')),
    ('cm', _('Centimeters')),
    ('m', _('Meters')),
    ('Km', _('Kilometers')),
    ('other', _('Other')),
]

PRODUCT_MEASURE_UNIT_CATEGORY_CHOICES = [
    ('pieces', _('Pieces')),
    ('g', _('grams')),
    ('Kg', _('Kilograms')),
    ('Ton', _('Tons')),
    ('ml', _('milliliters')),
    ('L', _('Liters')),
    ('cm', _('Centimeters')),
    ('m', _('Meters')),
    ('Km', _('Kilometers')),
    ('other', _('Other')),
]

SUPPLY_CATEGORY_CHOICES = [
    ('packaging_containment', _('Packaging Containment')),
    ('packaging_complement', _('Packaging Complement')),
    ('packaging_separator', _('Packaging Separator')),
    ('packaging_presentation', _('Packaging Presentation')),
    ('packaging_presentation_complement', _('Packaging Presentation Complement')),
    ('packaging_protection', _('Packaging Protection')),
    ('packaging_pallet', _('Packaging Pallet')),
    ('packaging_pallet_complement', _('Packaging Pallet Complement')),
    ('packaging_labeling', _('Packaging Labeling')),
    ('packaging_storage', _('Packaging Storage')),
    ('packhouse_stationery', _('Packhouse Stationery')),
    ('packhouse_cleaning', _('Packhouse Cleaning')),
    ('packhouse_maintenance', _('Packhouse Maintenance')),
    ('packhouse_transport', _('Packhouse Transport')),
    ('packhouse_fuel', _('Packhouse Fuel')),
    ('packhouse_tools', _('Packhouse Tools')),
    ('harvest_container', _('Harvest Container')),
    ('other', _('Other')),
]

SUPPLY_TRANSACTION_KIND_CHOICES = [
    ('inbound', _('Inbound')),
    ('outbound', _('Outbound')),
]

SUPPLY_TRANSACTION_CATEGORY_CHOICES = [
    ('adjustment_inventory', _('Adjustment Inventory')),
    ('packing', _('Packing')),
    ('repacking', _('Repacking')),
    ('purchase', _('Purchase')),
    ('sale', _('Sale')),
    ('transfer', _('Transfer')),
    ('return', _('Return')),
    ('other', _('Other')),
]
