from django.apps import AppConfig


class CommonUsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "common.users"

    def ready(self):
        from . import signals
