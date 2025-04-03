from django.utils.translation import gettext_lazy as _

STATUS_CHOICES = [
    ('open', _('Open')),
    ('ready', _('Ready')),
    ('closed', _('Closed')),
    ('canceled', _('Canceled')),
]

DATA_TYPE_CHOICES = [
    ('text', _('Text')),
    ('int', _('Integer')),
    ('number', _('Decimal')),
    ('date', _('Date')),
    ('checkbox', _('Checkbox')),
]

