import os
import json
import uuid
from django.conf import settings
from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from .utils import (uuid_file_path, validate_geom_vector_file, set_image_path, fix_format, fix_crs, to_polygon,
                    to_multipolygon, get_geom_from_file)
from django.utils import timezone
from .gee import get_rgb_image, get_ndvi_image, get_ndvi_difference_image
import tempfile
from django.core.files import File
from django.contrib.gis.geos import GEOSGeometry
from .gee import plot_multipolygon
from PIL import Image
import io
from common.profiles.models import ProducerProfile
# Create your models here.


class Parcel(models.Model):
    """
    A model to store parcel data.
    """

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateField(auto_now_add=True)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=100)
    file = models.FileField(upload_to=uuid_file_path, validators=[validate_geom_vector_file], null=True, blank=True)
    geom = models.MultiPolygonField(srid=settings.EUDR_DATA_FEATURES_SRID, null=True, blank=True)
    buffer_extent = models.JSONField(null=True, blank=True, editable=False)
    producer = models.ForeignKey(ProducerProfile, on_delete=models.PROTECT)

    delete_due_to_exception = False
    save_due_to_update_geom = False

    def __str__(self):
        return f"{self.uuid}: {self.name}"

    def clean(self):
        if self.pk is None and bool(self.file) == bool(self.geom):
            raise ValidationError("Must provide either a file or a geometry. Not both or none.")

    @receiver(pre_save, sender='parcels.Parcel')
    def check_file_change(sender, instance, **kwargs):
        print("check_file_change")
        if instance.pk:
            try:
                old_instance = sender.objects.get(pk=instance.pk)
                if old_instance.file != instance.file:
                    instance.save_due_to_update_geom = True
            except sender.DoesNotExist:
                pass

    @receiver(post_save, sender='parcels.Parcel')
    def set_geom_from_file(sender, instance, created, **kwargs):
        """
        Update the geom field of the RawVector instance with the geometry
        from the uploaded file.
        """

        try:
            if created and instance.file:
                fix_format(instance)
                fix_crs(instance)
                to_polygon(instance)
                to_multipolygon(instance)

                if instance.save_due_to_update_geom:
                    instance.geom = get_geom_from_file(instance)
                    # buffer_extent = GEOSGeometry(instance.geom).buffer(0.002)
                    # instance.buffer_extent = str(list(buffer_extent.extent))
                    instance.save()
            elif not created and instance.file and instance.save_due_to_update_geom:
                print("Updating")
                fix_format(instance)
                fix_crs(instance)
                to_polygon(instance)
                to_multipolygon(instance)

                instance.geom = get_geom_from_file(instance)
                instance.save_due_to_update_geom = False
                instance.save()


        except Exception as e:
            instance.file.close()
            instance.delete_due_to_exception = True
            if os.path.exists(instance.file.path):
                os.remove(instance.file.path)
            raise ValidationError(e)

    class Meta:
        verbose_name = "Parcel"
        verbose_name_plural = "Parcels"
