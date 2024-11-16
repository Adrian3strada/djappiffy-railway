from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from django.core.exceptions import ValidationError
import os
from .utils import fix_format, fix_crs, to_polygon, to_multipolygon, get_geom_from_file


@receiver(pre_save, sender='certiffy.RawVector')
def presave_rawvector(sender, instance, **kwargs):
    """
    Ensure that the file name matches the UUID before saving.
    """

    if instance.pk and not instance.save_due_to_update_geom:
        raise ValidationError("No se permite modificar registros RawVector existentes.")


@receiver(post_save, sender='certiffy.RawVector')
def update_geom(sender, instance, created, **kwargs):
    """
    Update the geom field of the RawVector instance with the geometry
    from the uploaded file.
    """

    try:
        if created:
            fix_format(instance)
            fix_crs(instance)
            to_polygon(instance)
            to_multipolygon(instance)

            if instance.save_due_to_update_geom:
                instance.geom = get_geom_from_file(instance)
                # buffer_extent = GEOSGeometry(instance.geom).buffer(0.002)
                # instance.buffer_extent = str(list(buffer_extent.extent))
                instance.save()

    except Exception as e:
        instance.file.close()
        instance.delete_due_to_exception = True
        if os.path.exists(instance.file.path):
            os.remove(instance.file.path)
        raise ValidationError(e)
