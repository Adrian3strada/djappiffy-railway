from django.utils.translation import gettext_lazy as _

STATUS_CHOICES = [
    ('pending', _('Pending')),
    ('printed', _('Printed')),
    ('scanned', _('Scanned')),
    ('discarded', _('Discarded')),
]