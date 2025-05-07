from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PackingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'packhouses.packing'
    verbose_name = _('Packing')
