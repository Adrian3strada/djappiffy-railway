from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PackhouseSettingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'packhouses.packhouse_settings'
    verbose_name = _('Catalogs settings')
