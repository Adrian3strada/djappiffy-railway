from django.apps import AppConfig


class ReceivingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'packhouses.receiving'

    def ready(self):
        from . import signals
