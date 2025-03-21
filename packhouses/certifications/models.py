import os
from django.db import models
from datetime import datetime
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from packhouses.catalogs.models import Organization
from common.base.models import CertificationEntity
from django.core.validators import FileExtensionValidator
from common.mixins import CleanDocumentsMixin

class Certification(models.Model):
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)
    certification_entity = models.ForeignKey(CertificationEntity, verbose_name=_('Certification Entity'), on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.certification_entity}"

    class Meta:
        verbose_name = _('Certification')
        verbose_name_plural = _('Certifications')
        ordering = ('organization', 'certification_entity')
        constraints = [
            models.UniqueConstraint(fields=['organization','certification_entity'], name='unique_organization_certification_entity'),
        ]

def certification_file_path(instance, filename):

    organization_name = slugify(instance.certification.organization.name).replace(" ", "")
    entity = slugify(instance.certification.certification_entity.entity).replace(" ", "")
    certification = slugify(instance.certification.certification_entity.certification).replace(" ", "")
    year = datetime.now().year
    file_extension = os.path.splitext(filename)[1]

    return f'{organization_name}/certifications/{entity}_{certification}_{year}_{filename}{file_extension}'

class CertificationDocument(CleanDocumentsMixin, models.Model):
    route = models.FileField(
        upload_to=certification_file_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        verbose_name=_('Certification')
        )
    registration_date = models.DateField()
    expiration_date = models.DateField()
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    certification = models.ForeignKey(Certification, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.route} -- {self.registration_date}  -- {self.expiration_date}  -- {self.certification}"

    class Meta:
        verbose_name = _('Certification Document')
        verbose_name_plural = _('Certifications Documents')