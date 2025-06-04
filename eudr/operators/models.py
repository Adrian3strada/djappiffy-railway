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
from common.profiles.models import EudrOperatorProfile
from cities_light.models import City, Region, Country
from django.utils.translation import gettext_lazy as _

# EXPORTER EUDR OPERATORS 

class OperatorParcel(models.Model):
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
    eudr_operator = models.ForeignKey(EudrOperatorProfile, on_delete=models.PROTECT)

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
            last_ooid = OperatorParcel.objects.filter(eudr_operator=self.eudr_operator).aggregate(models.Max('ooid'))[
                'ooid__max']
            self.ooid = (last_ooid or 0) + 1

    @receiver(post_save, sender='operators.OperatorParcel')
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
        verbose_name = "Operator Parcel"
        verbose_name_plural = "Operator Parcels"
        ordering = ('eudr_operator', 'ooid')


class ProductionInterval(models.Model):
    
    operator_parcel = models.ForeignKey(
        OperatorParcel,
        on_delete=models.PROTECT,
        verbose_name=_("Operator Parcel"),
        help_text=_("The parcel associated with this time production interval.")
    )
    start_date = models.DateField(
        verbose_name=_("Start date"),
        help_text=_("Start of the time production interval.")
    )
    end_date = models.DateField(
        verbose_name=_("End date"),
        help_text=_("End of the time production interval.")
    )

    class Meta:
        verbose_name = _("Production interval")
        verbose_name_plural = _("Production intervals")
        ordering = ['start_date']

    def __str__(self):
        return f"{self.operator_parcel} ({self.start_date} → {self.end_date})"
    

class LegalCompliance(models.Model): # Información del cumplimiento de la legislación pertinente del país de producción.

    operator_parcel = models.ForeignKey(
        OperatorParcel,
        on_delete=models.PROTECT,
        verbose_name=_('Operator Parcel'),
        help_text=_('Operator parcel related to this compliance record.'),
    )

    land_use_right = models.CharField(
        max_length=30,
        verbose_name=_('Land use right'),
        help_text=_('E.g. legal title, lease, community agreement'),
    )

    third_party_rights = models.FileField(
        upload_to='eudr_operators/compliance_documents/third_party_rights/', 
        verbose_name=_('Third-party rights (shapefile)'),
        help_text=_('Upload a ZIP shapefile or related document evidencing third-party rights.'),
        blank=True,
        null=True,
    )

    labor_and_human_rights = models.FileField(
        upload_to='eudr_operators/compliance_documents/labor_rights/',
        verbose_name=_('Labor & Human Rights (PDF)'),
        help_text=_('Upload a PDF document showing protection of labor and human rights.'),
        blank=True,
        null=True,
    )

    free_prior_informed_consent = models.FileField(
        upload_to='edur_operators/compliance_documents/fpic/',
        verbose_name=_('Free, Prior and Informed Consent (PDF)'),
        help_text=_('Upload a PDF document evidencing FPIC compliance.'),
        blank=True,
        null=True,
    )

    environmental_protection = models.FileField(
        upload_to='edur_operators/compliance_documents/environmental_protection/',
        verbose_name=_('Environmental protection (shapefile)'),
        help_text=_('Upload a ZIP shapefile showing environmental protection areas or measures.'),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _('Legal compliance')
        verbose_name_plural = _('Legal compliances')

