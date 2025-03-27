from django.utils.translation import gettext_lazy as _

ORDER_ITEMS_KIND_CHOICES = [
    ('product_measure_unit', _('Product measure unit')),
    ('product_packaging', _('Product packaging')),
    ('product_pallet', _('Product pallet')),
]

ORDER_ITEMS_PRICING_CHOICES = [
    ('product_measure_unit', _('Product measure unit')),
    ('product_packaging', _('Product packaging')),
    ('product_presentation', _('Product presentation')),
]

ORDER_ITEMS_PRICE_MEASURE_UNIT_CATEGORY_CHOICES = [
    ('g', _('grams')),
    ('Kg', _('Kilograms')),
    ('Ton', _('Tons')),
    ('ml', _('milliliters')),
    ('L', _('Liters')),
]
