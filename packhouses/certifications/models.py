import os
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from packhouses.catalogs.models import Organization
from common.base.models import CertificationEntity
from django.core.validators import FileExtensionValidator

class Certifications(models.Model):
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)
    certification_entity = models.ForeignKey(CertificationEntity, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.certification_entity}"

    class Meta:
        verbose_name = _('Certification')
        verbose_name_plural = _('Certifications')
        ordering = ('organization', 'certification_entity')
        constraints = [
            models.UniqueConstraint(fields=['certification_entity'], name='certification_unique_certification_entity_organization'),
        ]

# class CertificationsDocuments(models.Model):
#     certification = models.FileField(
#         upload_to='certifications/certifications/', 
#         validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
#         verbose_name=_('Certification')
#         )
#     registration_date = models.DateField()
#     expiration_date = models.DateField()
#     certification = models.ForeignKey(Certifications, on_delete=models.CASCADE)

#     def __str__(self):
#         return f"{self.certification} -- {self.registration_date}  -- {self.expiration_date}  -- {self.certification}"
