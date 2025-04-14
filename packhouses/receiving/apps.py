from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class ReceivingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'packhouses.receiving'
    verbose_name = _('Receiving')
