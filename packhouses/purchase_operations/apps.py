from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PurchaseOperationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'packhouses.purchase_operations'
    verbose_name = _('Purchase Operations')
