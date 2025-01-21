from django.utils.translation import gettext_lazy as _

ORDER_ITEMS_PRICE_CATEGORY_CHOICES = [
    ('unit', _('Per unit')),
    ('packaging', _('Per packaging')),
]

ORDER_ITEMS_PRICE_UNIT_CATEGORY_CHOICES = [
    ('g', _('gram')),
    ('Kg', _('Kilogram')),
    ('Ton', _('Tonelada?')),
    ('ml', _('milliliter')),
    ('L', _('Liter')),
]
