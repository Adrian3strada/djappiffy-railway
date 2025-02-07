from django.utils.translation import gettext_lazy as _

ORDER_ITEMS_PRICE_CATEGORY_CHOICES = [
    ('product_measure_unit', _('product measure unit')),
    ('product_packaging', _('Product packaging')),
]

ORDER_ITEMS_PRICE_MEASURE_UNIT_CATEGORY_CHOICES = [
    ('g', _('grams')),
    ('Kg', _('Kilograms')),
    ('Ton', _('Tons')),
    ('ml', _('milliliters')),
    ('L', _('Liters')),
]
