from django.db import models
from organizations.models import Organization

from ..catalogs.models import Market, ProductSize, Packaging, ProductPackaging, ProductMarketClass, ProductRipeness
from ..hrm.models import Employee
from ..receiving.models import Batch
from django.utils.translation import gettext_lazy as _
import uuid

# Create your models here.


class PackerLabel(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    employee = models.ForeignKey(Employee, verbose_name=_('Employee'), on_delete=models.PROTECT)
    scanned_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('Packer label')
        verbose_name_plural = _('Packer labels')

    def __str__(self):
        scanned_status = "Scanned" if self.scanned_at else "Not Scanned"
        return f"{self.employee.id}-{self.uuid} | {scanned_status}"


class PackerEmployeeManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            employeejobposition__job_position__category="packer"
        )


class PackerEmployee(Employee):
    objects = PackerEmployeeManager()

    class Meta:
        proxy = True
        verbose_name = _("Packer Employee")
        verbose_name_plural = _("Packer Employees")

    def position(self):
        job_position = self.employeejobposition
        return job_position.job_position.name if job_position else "N/A"

    def full_name_column(self, obj):
        return obj.full_name

    full_name_column.short_description = _("Full name")


class Package(models.Model):

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    packer = models.ForeignKey(PackerEmployee, verbose_name=_('Packer'), on_delete=models.PROTECT)
    scanned_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        scanned_status = "Scanned" if self.scanned_at else "Not Scanned"
        return f"{self.packer.id}-{self.uuid} | {scanned_status}"

    class Meta:
        verbose_name = _('Package')
        verbose_name_plural = _('Packages')


class Packing(models.Model):
    batch = models.ForeignKey(Batch, verbose_name=_('Batch'), on_delete=models.PROTECT)
    product_size = models.ForeignKey(ProductSize, verbose_name=_('Product size'), on_delete=models.PROTECT)
    product_phenology = models.ForeignKey(ProductPhenologyKind, verbose_name=_('Product phenology'), on_delete=models.PROTECT, null=True, blank=False)
    product_market_class = models.ForeignKey(ProductMarketClass, verbose_name=_('Product market class'), on_delete=models.PROTECT, null=True, blank=False)
    product_ripeness = models.ForeignKey(ProductRipeness, verbose_name=_('Product ripeness'), on_delete=models.PROTECT, null=True, blank=True)




    quantity = models.FloatField(verbose_name=_('Quantity'), validators=[MinValueValidator(0.01)])





    product_packaging = models.ForeignKey(ProductPackaging, verbose_name=_('Product packaging'), on_delete=models.PROTECT)
    product_packaging_weight = models.FloatField(_("Product packaging weight"))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id} - {self.batch} - {self.batch.incomingproduct.scheduleharvest.product.name} - {self.product_size} - {self.batch.incomingproduct.scheduleharvest.market.name} - {self.product_packaging}"

    class Meta:
        verbose_name = _('Packing')
        verbose_name_plural = _('Packings')
