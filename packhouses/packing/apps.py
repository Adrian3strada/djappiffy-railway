from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save, post_delete, pre_save


class PackingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'packhouses.packing'
    verbose_name = _('Packing')

    def ready(self):
        from .signals import capture_previous_status, handle_packing_package_pre_save, handle_packing_package_post_save, handle_packing_package_post_delete
        from .models import PackingPackage

        pre_save.connect(capture_previous_status, sender=PackingPackage)
        pre_save.connect(handle_packing_package_pre_save, sender=PackingPackage)
        post_save.connect(handle_packing_package_post_save, sender=PackingPackage)
        post_delete.connect(handle_packing_package_post_delete, sender=PackingPackage)
