from django.apps import AppConfig


class CertificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'packhouses.certifications'

    def ready(self):
        from . import signals
