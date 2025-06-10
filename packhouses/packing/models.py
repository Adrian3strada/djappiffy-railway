import datetime

from django.core.validators import MinValueValidator
from django.db import models, transaction
from organizations.models import Organization
from ..catalogs.models import Market, ProductSize, ProductPackaging, SizePackaging, ProductMarketClass, ProductRipeness, \
    ProductPhenologyKind, Product, ProductPackagingPallet
from ..hrm.models import Employee
from ..receiving.models import Batch
from django.utils.translation import gettext_lazy as _
from common.settings import STATUS_CHOICES
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


class ScanPackage(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    packer = models.ForeignKey(PackerEmployee, verbose_name=_('Packer'), on_delete=models.PROTECT)
    created_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        scanned_status = "Scanned" if self.created_at else "Not Scanned"
        return f"{self.packer.id}-{self.uuid} | {scanned_status}"

    class Meta:
        verbose_name = _('Package')
        verbose_name_plural = _('Packages')


class PackingPallet(models.Model):
    ooid = models.PositiveIntegerField(verbose_name=_('OOID'), null=True, blank=True)
    market = models.ForeignKey(Market, verbose_name=_('Market'), on_delete=models.PROTECT)
    # product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.PROTECT)
    product_size = models.ForeignKey(ProductSize, verbose_name=_('Product size'), on_delete=models.PROTECT)
    product_phenology = models.ForeignKey(ProductPhenologyKind, verbose_name=_('Product phenology'), on_delete=models.PROTECT, null=True, blank=False)
    product_market_class = models.ForeignKey(ProductMarketClass, verbose_name=_('Product market class'), on_delete=models.PROTECT, null=True, blank=False)
    product_ripeness = models.ForeignKey(ProductRipeness, verbose_name=_('Product ripeness'), on_delete=models.PROTECT, null=True, blank=True)
    size_packaging = models.ForeignKey(SizePackaging, verbose_name=_('Size packaging'), on_delete=models.PROTECT)
    product_packaging_quantity = models.PositiveIntegerField(verbose_name=_('Packaging quantity'), validators=[MinValueValidator(1)])
    product_packaging_pallet = models.ForeignKey(ProductPackagingPallet, verbose_name=_('Product packaging pallet'), on_delete=models.PROTECT, null=True, blank=False)
    status = models.CharField(max_length=20, default='open', verbose_name=_('Status'), choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)
    # cajas -- @property / invref
    # kg -- @property / invref

    def __str__(self):
        return f"{self.ooid} - {self.market} - {self.product_size} ({self.product})"

    def save(self, *args, **kwargs):
        if self.ooid is None:
            with transaction.atomic():
                last = (PackingPallet.objects.filter(organization=self.organization).order_by('-ooid').first())
                self.ooid = (last.ooid + 1) if last else 1
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('Packing Pallet')
        verbose_name_plural = _('Packing Pallets')


class PackingPackage(models.Model):
    ooid = models.PositiveIntegerField(verbose_name=_('Package ID'), null=True, blank=True)
    batch = models.ForeignKey(Batch, verbose_name=_('Batch'), on_delete=models.PROTECT)
    # , limit_choices_to={'parent__isnull': True, 'is_available_for_processing': True} ?
    market = models.ForeignKey(Market, verbose_name=_('Market'), on_delete=models.PROTECT)
    # product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.PROTECT)
    product_phenology = models.ForeignKey(ProductPhenologyKind, verbose_name=_('Product phenology'),on_delete=models.PROTECT, null=True, blank=False)
    product_size = models.ForeignKey(ProductSize, verbose_name=_('Product size'), on_delete=models.PROTECT)
    product_market_class = models.ForeignKey(ProductMarketClass, verbose_name=_('Product market class'), on_delete=models.PROTECT, null=True, blank=False)
    product_ripeness = models.ForeignKey(ProductRipeness, verbose_name=_('Product ripeness'), on_delete=models.PROTECT, null=True, blank=True)

    size_packaging = models.ForeignKey(SizePackaging, verbose_name=_('Size packaging'), on_delete=models.PROTECT)
    product_weight_per_packaging = models.FloatField(verbose_name=_('Product weight per packaging'), validators=[MinValueValidator(0.01)])
    product_presentations_per_packaging = models.PositiveIntegerField(verbose_name=_('Product presentations per packaging'), null=True, blank=False)
    product_pieces_per_presentation = models.PositiveIntegerField(verbose_name=_('Product pieces per presentation'), null=True, blank=False)
    packaging_quantity = models.PositiveIntegerField(verbose_name=_('Packaging quantity'), validators=[MinValueValidator(1)])

    processing_date = models.DateField(default=datetime.datetime.today, verbose_name=_('Processing date'))
    status = models.CharField(max_length=20, default='open', verbose_name=_('Status'), choices=STATUS_CHOICES)
    packing_pallet = models.ForeignKey(PackingPallet, verbose_name=_('Packing Pallet'), on_delete=models.PROTECT, null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)
    # cajas -- packaging_quantity
    # kg -- @property packaging_quantity * product_weight_per_packaging

    @property
    def packing_package_weight(self):
        return self.packaging_quantity * self.product_weight_per_packaging

    @property
    def batch_number(self):
        return self.batch.ooid

    @property
    def guide_number(self):
        return self.ooid

    @property
    def product_producer(self):
        return self.batch.incomingproduct.scheduleharvest.orchard.producer if self.batch and self.batch.incomingproduct and self.batch.incomingproduct.scheduleharvest and self.batch.incomingproduct.scheduleharvest.orchard and self.batch.incomingproduct.scheduleharvest.orchard.producer else None

    @property
    def product_provider(self):
        return self.batch.incomingproduct.scheduleharvest.product_provider if self.batch and self.batch.incomingproduct and self.batch.incomingproduct.scheduleharvest and self.batch.incomingproduct.scheduleharvest.product_provider else None

    @property
    def orchard(self):
        return self.batch.incomingproduct.scheduleharvest.orchard if self.batch and self.batch.incomingproduct and self.batch.incomingproduct.scheduleharvest and self.batch.incomingproduct.scheduleharvest.orchard else None

    @property
    def orchard_certifications(self):
        if self.batch and self.batch.incomingproduct and self.batch.incomingproduct.scheduleharvest and self.batch.incomingproduct.scheduleharvest.orchard:
            all_certifications = self.batch.incomingproduct.scheduleharvest.orchard.orchardcertification_set.filter(is_enabled=True, expiration_date__gte=datetime.datetime.today())
            if all_certifications.exists():
                return ", ".join([f"{certification.certification_kind.name} ({certification.certification_number})" for certification in all_certifications])
        return "-"

    @property
    def orchard_registry_code(self):
        return self.batch.incomingproduct.scheduleharvest.orchard.code if self.batch and self.batch.incomingproduct and self.batch.incomingproduct.scheduleharvest and self.batch.incomingproduct.scheduleharvest.orchard else None

    def orchard_location(self):
        if self.batch and self.batch.incomingproduct and self.batch.incomingproduct.scheduleharvest and self.batch.incomingproduct.scheduleharvest.orchard:
            orchard = self.batch.incomingproduct.scheduleharvest.orchard
            return f"{orchard.district.name} - {orchard.city.name}, ({orchard.state.name})"
        return "-"

    @property
    def destination_market(self):
        return self.market.name if self.market else "-"

    @property
    def harvest_crews(self):
        if self.batch and self.batch.incomingproduct and self.batch.incomingproduct.scheduleharvest:
            crews = self.batch.incomingproduct.scheduleharvest.scheduleharvestharvestingcrew_set.all()
            if crews.exists():
                return ", ".join([f"{crew.harvesting_crew.name} ({crew.harvesting_crew.crew_chief.name})" for crew in crews])
        return "-"

    def __str__(self):
        return f"{self.ooid} - {self.batch} - {self.packaging_quantity}"

    def save(self, *args, **kwargs):
        if self.ooid is None:
            with transaction.atomic():
                last = (PackingPackage.objects.filter(organization=self.organization).order_by('-ooid').first())
                self.ooid = (last.ooid + 1) if last else 1
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('Packing Package')
        verbose_name_plural = _('Packing Packages')
