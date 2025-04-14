from django.utils.translation import gettext_lazy as _

PRODUCT_SIZE_CATEGORY_CHOICES = [
    ('size', _('Size')),
    ('mix', _('Mix')),
    ('waste', _('Waste')),
    ('biomass', _('Biomass')),
]

PRODUCT_PACKAGING_CATEGORY_CHOICES = [
    ('single', _('Single packaging')),
    ('presentation', _('With presentation')),
]

PRODUCT_PRICE_MEASURE_UNIT_CATEGORY_CHOICES = [
    ('g', _('grams')),
    ('Kg', _('Kilograms')),
    ('Ton', _('Tons')),
    ('ml', _('milliliters')),
    ('L', _('Liters')),
]

CLIENT_KIND_CHOICES = [
    ('packhouse', _('Packhouse client')),
    ('maquiladora', _('Maquiladora client')),
]

ORCHARD_PRODUCT_CLASSIFICATION_CHOICES = [
    ('conventional', _('Conventional')),
    ('organic', _('Organic')),
]
