from django.utils.translation import gettext_lazy as _

ORDER_ITEMS_PRICE_CATEGORY_CHOICES = [
    ('unit', _('Per unit')),
    ('packaging', _('Per packaging')),
]

ORDER_ITEMS_PRICE_MEASURE_UNIT_CATEGORY_CHOICES = [
    ('g', _('grams')),
    ('Kg', _('Kilograms')),
    ('Ton', _('Tons')),
    ('ml', _('milliliters')),
    ('L', _('Liters')),
]
