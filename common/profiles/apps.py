from django.apps import AppConfig


class CommonProfilesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'common.profiles'

    def ready(self):
        from . import signals