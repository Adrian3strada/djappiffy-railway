from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PurchaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'packhouses.purchases'
    verbose_name = _('Purchases')

    def ready(self):
        import packhouses.purchases.signals
