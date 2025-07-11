import datetime
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from organizations.models import Organization
from ..catalogs.models import Market, ProductSize, ProductPackaging, SizePackaging, ProductMarketClass, ProductRipeness, \
    ProductPhenologyKind, Product, Pallet
from ..hrm.models import Employee
from ..receiving.models import Batch
from django.utils.translation import gettext_lazy as _
from common.settings import STATUS_CHOICES
import uuid
from django.db.models import Sum
from collections import defaultdict


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
    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.PROTECT)
    market = models.ForeignKey(Market, verbose_name=_('Market'), on_delete=models.PROTECT)
    product_sizes = models.ManyToManyField(ProductSize, verbose_name=_('Product sizes'))
    pallet = models.ForeignKey(Pallet, verbose_name=_('Pallet'), on_delete=models.PROTECT, null=True, blank=False)
    status = models.CharField(max_length=20, default='open', verbose_name=_('Status'), choices=STATUS_CHOICES)
    is_repacked = models.BooleanField(default=False, verbose_name=_('Is repacked'))
    created_at = models.DateTimeField(auto_now_add=True)
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.ooid} - {self.market} - {self.pallet.name} (Q:{self.pallet_packages_sum_quantity}|{self.pallet.max_packages_quantity}) - {', '.join(self.product_sizes.all().values_list('name', flat=True))}"

    @property
    def pallet_sum_weight(self):
        return round(sum(pkg.packing_package_sum_weight for pkg in self.packingpackage_set.all()), 2)

    @property
    def pallet_batch_weights(self):
        batch_totals = defaultdict(float)

        for pkg in self.packingpackage_set.select_related('batch').all():
            batch_totals[pkg.batch] += pkg.packing_package_sum_weight

        return dict(batch_totals)

    @property
    def pallet_supplies(self):
        totals = defaultdict(float)

        # 1. Sumar insumos de cada paquete
        packages = self.packingpackage_set.select_related(
            'size_packaging__product_packaging__packaging_supply',
            'size_packaging__product_presentation__presentation_supply'
        ).prefetch_related(
            'size_packaging__product_packaging__productpackagingcomplementarysupply_set__supply',
            'size_packaging__product_presentation__productpresentationcomplementarysupply_set__supply'
        )

        for pkg in packages:
            for item in pkg.package_supplies:
                supply = item['supply']
                quantity = item['quantity']
                totals[supply] += float(quantity)

        # 2. Agregar 1 unidad del insumo principal del pallet
        if self.pallet and self.pallet.supply:
            totals[self.pallet.supply] += 1.0

        # 3. Agregar insumos complementarios del pallet
        if self.pallet:
            for comp in self.pallet.palletcomplementarysupply_set.select_related('supply').all():
                totals[comp.supply] += float(comp.quantity)

        # 4. Aplicar formato final
        return {supply: int(qty) if qty == int(qty) else round(qty, 2) for supply, qty in totals.items()}

    @property
    def pallet_packages_sum_quantity(self):
        if self.pk:
            return self.packingpackage_set.all().aggregate(total_quantity=Sum('packaging_quantity'))['total_quantity'] or 0
        return 0

    def save(self, *args, **kwargs):
        if self.ooid is None:
            with transaction.atomic():
                last = (PackingPallet.objects.filter(organization=self.organization).order_by('-ooid').first())
                self.ooid = (last.ooid + 1) if last else 1

        if self.id and self.status == 'closed':
            self.packingpackage_set.all().update(status='closed')
        if self.id and self.is_repacked:
            self.packingpackage_set.all().update(is_repacked=True)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('Packing Pallet')
        verbose_name_plural = _('Packing Pallets')


class PackingPackage(models.Model):
    ooid = models.PositiveIntegerField(verbose_name=_('Package ID'), null=True, blank=True)
    batch = models.ForeignKey(Batch, verbose_name=_('Batch'), on_delete=models.PROTECT)
    market = models.ForeignKey(Market, verbose_name=_('Market'), on_delete=models.PROTECT)
    product_size = models.ForeignKey(ProductSize, verbose_name=_('Product size'), on_delete=models.PROTECT)
    product_market_class = models.ForeignKey(ProductMarketClass, verbose_name=_('Product market class'),
                                             on_delete=models.PROTECT, null=True, blank=False)
    product_ripeness = models.ForeignKey(ProductRipeness, verbose_name=_('Product ripeness'), on_delete=models.PROTECT,
                                         null=True, blank=True)
    size_packaging = models.ForeignKey(SizePackaging, verbose_name=_('Size packaging'), on_delete=models.PROTECT)
    product_weight_per_packaging = models.FloatField(verbose_name=_('Product weight per packaging'),
                                                     validators=[MinValueValidator(0.01)])
    product_presentations_per_packaging = models.PositiveIntegerField(
        verbose_name=_('Product presentations per packaging'), null=True, blank=False)
    product_pieces_per_presentation = models.PositiveIntegerField(verbose_name=_('Product pieces per presentation'),
                                                                  null=True, blank=False)
    packaging_quantity = models.PositiveIntegerField(verbose_name=_('Packaging quantity'),
                                                     validators=[MinValueValidator(1)])
    processing_date = models.DateField(default=datetime.datetime.today, verbose_name=_('Processing date'))
    packing_pallet = models.ForeignKey(PackingPallet, verbose_name=_('Packing Pallet'), on_delete=models.CASCADE,
                                       null=True, blank=True)
    status = models.CharField(max_length=20, default='open', verbose_name=_('Status'), choices=STATUS_CHOICES)
    is_repacked = models.BooleanField(default=False, verbose_name=_('Is repacked'))
    created_at = models.DateField(auto_now_add=True)
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    @property
    def package_supplies(self):
        supplies = []
        main_supply = {'supply': self.size_packaging.product_packaging.packaging_supply,
                       'quantity': self.packaging_quantity}
        complementary_supplies = [
            {'supply': supply.supply, 'quantity': supply.quantity * self.packaging_quantity} for supply in
            self.size_packaging.product_packaging.productpackagingcomplementarysupply_set.all()
        ]
        supplies.append(main_supply)
        supplies.extend(complementary_supplies)
        if self.size_packaging.category == 'presentation':
            presentation_supply = {'supply': self.size_packaging.product_presentation.presentation_supply,
                                   'quantity': self.product_presentations_per_packaging * self.packaging_quantity}
            presentation_complementary_supplies = [
                {'supply': supply.supply,
                 'quantity': self.product_presentations_per_packaging * self.packaging_quantity} for supply in
                self.size_packaging.product_presentation.productpresentationcomplementarysupply_set.all()
            ]
            supplies.append(presentation_supply)
            supplies.extend(presentation_complementary_supplies)
        return supplies if not self.is_repacked else []

    @property
    def packing_package_sum_weight(self):
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
            all_certifications = self.batch.incomingproduct.scheduleharvest.orchard.orchardcertification_set.filter(
                is_enabled=True, expiration_date__gte=datetime.datetime.today())
            if all_certifications.exists():
                return ", ".join(
                    [f"{certification.certification_kind.name} ({certification.certification_number})" for certification
                     in all_certifications])
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
                return ", ".join(
                    [f"{crew.harvesting_crew.name} ({crew.harvesting_crew.crew_chief.name})" for crew in crews])
        return "-"

    def __str__(self):
        return f"{self.ooid} - {self.batch} - {self.packaging_quantity}"

    def clean(self):
        super().clean()
        packing_package = PackingPackage.objects.get(pk=self.pk) if self.pk else None
        packaging_quantity = self.packaging_quantity if self.packaging_quantity else (
            packing_package.packaging_quantity if packing_package else None)
        if self.packing_pallet and packaging_quantity:
            if self.packing_pallet.pallet_packages_sum_quantity + packaging_quantity > self.packing_pallet.pallet.max_packages_quantity:
                remaining_packages_quantity = self.packing_pallet.pallet.max_packages_quantity - self.packing_pallet.pallet_packages_sum_quantity
                validation_error = _(
                    "The pallet cannot accommodate more packages than its maximum capacity. Remaining packages: {}|{}, Tried {}"
                ).format(remaining_packages_quantity, self.packing_pallet.pallet.max_packages_quantity,
                         packaging_quantity)
                raise ValidationError({'__all__': validation_error, 'packaging_quantity': validation_error,
                                       'packing_pallet': validation_error})

    def save(self, *args, **kwargs):
        if self.ooid is None:
            with transaction.atomic():
                if not self.organization_id:
                    self.organization = self.packing_pallet.organization if self.packing_pallet else None
                last = (PackingPackage.objects.filter(organization=self.organization).order_by('-ooid').first())
                self.ooid = (last.ooid + 1) if last else 1

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('Packing Package')
        verbose_name_plural = _('Packing Packages')


class UnpackingPallet(models.Model):
    packing_pallet = models.OneToOneField(PackingPallet, verbose_name=_('Packing Pallet'), on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"Unpacking Pallet {self.packing_pallet.ooid} - Unpacked at {self.created_at}"

    class Meta:
        verbose_name = _('Unpacking Pallet')
        verbose_name_plural = _('Unpacking Pallets')


class UnpackingBatch(models.Model):
    unpacking_pallet = models.OneToOneField(UnpackingPallet, verbose_name=_('Packing Package'), on_delete=models.CASCADE)
    initial_weight = models.FloatField(verbose_name=_('Original Weight'), validators=[MinValueValidator(0.1)])
    lost_weight = models.FloatField(verbose_name=_('Current Weight'), validators=[MinValueValidator(0.1)])
    return_weight = models.FloatField(verbose_name=_('Return Weight'), validators=[MinValueValidator(0.1)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id} - Unpacking pallet {self.unpacking_pallet.packing_pallet.ooid} - Unpacked at {self.created_at}"

    class Meta:
        verbose_name = _('Unpacking Package')
        verbose_name_plural = _('Unpacking Packages')


class UnpackingSupply(models.Model):
    unpacking_pallet = models.OneToOneField(UnpackingPallet, verbose_name=_('Packing Package'), on_delete=models.CASCADE)
    supply = models.ForeignKey(ProductPackaging, verbose_name=_('Supply'), on_delete=models.PROTECT)
    initial_quantity = models.FloatField(verbose_name=_('Initial quantity'), validators=[MinValueValidator(0.1)])
    lost_quantity = models.FloatField(verbose_name=_('Lost quantity'), validators=[MinValueValidator(0.1)])
    return_quantity = models.FloatField(verbose_name=_('Return quantity'), validators=[MinValueValidator(0.1)])
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def quantity(self):
        return self.initial_quantity - self.lost_quantity - self.return_quantity
    def __str__(self):
        return f"Unpacking Supply {self.supply.name} - Quantity: {self.quantity}"

    class Meta:
        verbose_name = _('Unpacking Supply')
        verbose_name_plural = _('Unpacking Supplies')
