import os
import json
import uuid
from django.conf import settings
from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from .utils import (uuid_file_path, validate_geom_vector_file, fix_format, fix_crs, to_polygon,
                    to_multipolygon, get_geom_from_file)
from django.contrib.gis.geos import GEOSGeometry
from common.profiles.models import ProducerProfile
from cities_light.models import City, Region, Country

# Create your models here.


class Parcel(models.Model):
    """
    A model to store parcel data.
    """

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    ooid = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.PROTECT)
    state = models.ForeignKey(Region, on_delete=models.PROTECT)
    city = models.ForeignKey(City, on_delete=models.PROTECT)
    file = models.FileField(upload_to=uuid_file_path, validators=[validate_geom_vector_file], null=True, blank=True)
    geom = models.MultiPolygonField(srid=settings.EUDR_DATA_FEATURES_SRID, null=True, blank=True)
    buffer_extent = models.JSONField(null=True, blank=True)
    producer = models.ForeignKey(ProducerProfile, on_delete=models.PROTECT)

    delete_due_to_exception = False
    save_due_to_update_geom = False

    def __str__(self):
        return f"{self.uuid}: {self.name}"

    def geom_extent(self):
        if self.geom:
            return json.dumps(str(list(self.geom.extent)))
        return None

    def clean(self):
        if self.pk is None and bool(self.file) == bool(self.geom):
            raise ValidationError("Must provide either a file or a geometry. Not both or none.")

        if not self.ooid:
            # Obtener el último pseudo_id del mismo producer
            last_ooid = Parcel.objects.filter(producer=self.producer).aggregate(models.Max('ooid'))[
                'ooid__max']
            self.ooid = (last_ooid or 0) + 1

    @receiver(post_save, sender='parcels.Parcel')
    def set_geom_from_file(sender, instance, created, **kwargs):
        """
        Update the geom field of the RawVector instance with the geometry
        from the uploaded file.
        """
        if getattr(instance, 'save_due_to_update_geom', False):
            print("instance.save_due_to_update_geom", instance.save_due_to_update_geom)
            return

        try:
            if instance.file and not instance.save_due_to_update_geom:
                fix_format(instance)
                fix_crs(instance)
                to_polygon(instance)
                to_multipolygon(instance)

                instance.geom = get_geom_from_file(instance)
                buffer_extent = GEOSGeometry(instance.geom).buffer(0.002)
                instance.buffer_extent = str(list(buffer_extent.extent))
                print("instance.geom", instance.geom)
                instance.save_due_to_update_geom = True
                instance.save()
            else:
                print("instance.save_due_to_update_geom", instance.save_due_to_update_geom)

        except Exception as e:
            instance.file.close()
            instance.delete_due_to_exception = True
            if os.path.exists(instance.file.path):
                os.remove(instance.file.path)
            raise ValidationError(e)

    class Meta:
        verbose_name = "Parcel"
        verbose_name_plural = "Parcels"
        ordering = ('producer', 'ooid')
