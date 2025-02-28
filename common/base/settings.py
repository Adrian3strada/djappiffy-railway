from django.utils.translation import gettext_lazy as _

SUPPLY_USAGE_UNIT_KIND_CHOICES = [
    ('piece', _('Piece')),
    ('box', _('Box')),
    ('bag', _('Bag')),
    ('pallet', _('Pallet')),
    ('Km', _('Kilometers')),
    ('m', _('Meters')),
    ('cm', _('Centimeters')),
    ('Kg', _('Kilograms')),
    ('g', _('Grams')),
    ('l', _('Liters')),
    ('other', _('Other')),
]

PRODUCT_CAPACITY_MEASURE_UNIT_CATEGORY_CHOICES = [
    ('pieces', _('Pieces')),
    ('g', _('grams')),
    ('Kg', _('Kilograms')),
    ('Ton', _('Tons')),
    ('ml', _('milliliters')),
    ('L', _('Liters')),
]

SUPPLY_CATEGORY_CHOICES = [
    ('packaging_containment', _('Packaging Containment')),
    ('packaging_complement', _('Packaging Complement')),
    ('packaging_separator', _('Packaging Separator')),
    ('packaging_presentation', _('Packaging Presentation')),
    ('packaging_presentation_complement', _('Packaging Presentation Complement')),
    ('packaging_protection', _('Packaging Protection')),
    ('packaging_pallet', _('Packaging Pallet')),
    ('packaging_pallet_protection', _('Packaging Pallet Protection')),
    ('packaging_pallet_wrapping', _('Packaging Pallet Wrapping')),
    ('packaging_labeling', _('Packaging Labeling')),
    ('packaging_storage', _('Packaging Storage')),
    ('packhouse_stationery', _('Packhouse Stationery')),
    ('packhouse_cleaning', _('Packhouse Cleaning')),
    ('packhouse_maintenance', _('Packhouse Maintenance')),
    ('packhouse_transport', _('Packhouse Transport')),
    ('packhouse_fuel', _('Packhouse Fuel')),
    ('packhouse_tools', _('Packhouse Tools')),
    ('other', _('Other')),
]

