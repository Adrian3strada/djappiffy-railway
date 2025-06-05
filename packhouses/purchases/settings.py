from django.utils.translation import gettext_lazy as _

PURCHASE_SERVICE_CATEGORY_CHOICES = [
    ('time_period', _('TIME PERIOD')),
    ('for_batch', _('FOR BATCH')),
]

PURCHASE_CATEGORY_CHOICES = [
    ('purchase_order', _('PURCHASE ORDER')),
    ('service_order', _('SERVICE ORDER')),
]

FRUIT_PURCHASE_CATEGORY_CHOICES = [
    ('fixed', _('FIXED PRICE')),
    ('yield', _('YIELD-BASED PRICE')),
]

FRUIT_RECEIPT_KIND_CHOICES = [
    ('producer', _('PRODUCER')),
    ('provider', _('PROVIDER')),
]
