from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _



class GatheringConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'packhouses.gathering'
    verbose_name = _('Gathering')
