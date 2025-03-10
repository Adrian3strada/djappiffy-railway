
from django.db import models
from django.utils.translation import gettext_lazy as _
from common.base.models import ProductKind
from packhouses.catalogs.models import Product, Organization
from common.mixins import (CleanNameOrAliasAndOrganizationMixin)

class CertificationCatalog(models.Model):
    certifier = models.CharField(max_length=255)
    certification = models.CharField(max_length=255)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))

    def _str_(self):
        return f"{self.certifier} -- {self.certification} -- {self.is_enabled}"

class RequirementsCertification(models.Model):
    name = models.CharField(max_length=255)
    route = models.FileField(upload_to='documentos/', verbose_name=_('Document'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    certification_catalog = models.ForeignKey(CertificationCatalog, on_delete=models.CASCADE)

    def _str_(self):
        return f"{self.name} -- {self.is_enabled} -- {self.certification_catalog}"

# # class ReportsCertification(models.Model):
# #     name = models.CharField(max_length=255)
# #     method = models.CharField(max_length=255)
# #     is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
# #     certification_catalog = models.ForeignKey(CertificationCatalog, on_delete=models.CASCADE)

# #     def _str_(self):
# #         return f"{self.name} -- {self.method} -- {self.is_enabled} -- {self.certification_catalog}"

class CertificationProducts(models.Model): 
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    product_kind = models.ForeignKey(ProductKind, verbose_name=_('Product Kind'), on_delete=models.PROTECT)
    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.PROTECT)
    certification_catalog = models.ForeignKey(CertificationCatalog, verbose_name=_('Certification Catalog'), on_delete=models.CASCADE)

    def _str_(self):
        return f"{self.is_enabled} -- {self.product_kind} -- {self.product} -- {self.certification_catalog}"

class Certifications(CleanNameOrAliasAndOrganizationMixin, models.Model):
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)
    certification_catalog = models.ForeignKey(CertificationCatalog, on_delete=models.CASCADE)

    def _str_(self):
        return f"{self.company}  -- {self.certification_catalog}"

    class Meta:
        verbose_name = _('CertificationProducts')
        verbose_name_plural = _('CertificationProducts')
        ordering = ('organization', 'certification_catalog')
        constraints = [
            models.UniqueConstraint(fields=['organization'], name='CertificationProducts_unique_name_organization'),
        ]

class CertificationsDocuments(models.Model):
    certification = models.FileField(upload_to='documentos/', verbose_name=_('Certification'))
    registration_date = models.DateField()
    expiration_date = models.DateField()
    certification = models.ForeignKey(Certifications, on_delete=models.CASCADE)

    def _str_(self):
        return f"{self.certification} -- {self.registration_date}  -- {self.expiration_date}  -- {self.certification}"