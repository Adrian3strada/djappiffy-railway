from django.db import models
import os
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from common.base.models import ProductKind
from packhouses.catalogs.models import Product, Organization
from common.mixins import (CleanNameOrAliasAndOrganizationMixin, CleanNameAndProductMixin)
from django.core.validators import FileExtensionValidator

class CertificationCatalog(models.Model):
    certifier = models.CharField(max_length=255)
    certification = models.CharField(max_length=255)
    product_kind = models.ForeignKey(ProductKind, verbose_name=_('Product Kind'), null=True, blank=True, on_delete=models.PROTECT)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))

    def __str__(self):
        return f"{self.certifier} -- {self.product_kind} -- {self.certification}"

def certification_file_path(instance, filename):

    catalog_id = instance.certification_catalog.id
    catalog_certifier = slugify(instance.certification_catalog.certifier.replace(" ", ""))
    catalog_product_kind = slugify(instance.certification_catalog.product_kind).replace(" ", "")

    file_extension = os.path.splitext(filename)[1]
    file_name = slugify(instance.name.replace(" ", ""))

    return f'certifications/requirements/{catalog_id}_{catalog_product_kind}_{catalog_certifier}_{file_name}{file_extension}'

class RequirementsCertification(models.Model):
    name = models.CharField(max_length=255)
    route = models.FileField(
        upload_to=certification_file_path, 
        validators=[FileExtensionValidator(allowed_extensions=['docx'])],
        verbose_name=_('Document')
        )
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    certification_catalog = models.ForeignKey(CertificationCatalog, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} -- {self.is_enabled} -- {self.certification_catalog}"

    def save(self, *args, **kwargs):
        try:
            old_instance = RequirementsCertification.objects.get(pk=self.pk)
            if old_instance.route and old_instance.route != self.route:
                if os.path.isfile(old_instance.route.path):
                    os.remove(old_instance.route.path)
        except RequirementsCertification.DoesNotExist:
            pass 

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.route and os.path.isfile(self.route.path):
            os.remove(self.route.path)
        super().delete(*args, **kwargs)

class Certifications(models.Model):
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)
    certification_catalog = models.ForeignKey(CertificationCatalog, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.certification_catalog}"

#     class Meta:
#         verbose_name = _('Certifications')
#         verbose_name_plural = _('Certifications')
#         ordering = ('organization', 'certification_catalog')
#         constraints = [
#             models.UniqueConstraint(fields=['certification_catalog', 'organization'], name='CertificationProducts_unique_name_organization'),
#         ]

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

# ---------------
# # class ReportsCertification(models.Model):
# #     name = models.CharField(max_length=255)
# #     method = models.CharField(max_length=255)
# #     is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
# #     certification_catalog = models.ForeignKey(CertificationCatalog, on_delete=models.CASCADE)

# #     def _str_(self):
# #         return f"{self.name} -- {self.method} -- {self.is_enabled} -- {self.certification_catalog}"