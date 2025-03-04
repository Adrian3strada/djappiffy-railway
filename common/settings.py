from django.utils.translation import gettext_lazy as _

STATUS_CHOICES = [
    ('open', _('Open')),
    ('ready', _('Ready')),
    ('closed', _('Closed')),
    ('canceled', _('Canceled')),
]

WEEKDAYS_CHOICES = [
        ('Monday', _('Monday')),
        ('Tuesday', _('Tuesday')),
        ('Wednesday', _('Wednesday')),
        ('Thursday', _('Thursday')),
        ('Friday', _('Friday')),
        ('Saturday', _('Saturday')),
        ('Sunday', _('Sunday')),
    ]