from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class StorehouseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'packhouses.storehouse'
    verbose_name = _('Storehouse')
