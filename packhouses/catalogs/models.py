from django.db import models
from organizations.models import Organization
from cities_light.models import City, Country, Region
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django_ckeditor_5.fields import CKEditor5Field
from django.conf import settings
from common.billing.models import TaxRegime, LegalEntityCategory
from .utils import vehicle_year_choices, vehicle_validate_year


# Create your models here.


class Market(models.Model):
    name = models.CharField(max_length=100)
    management_cost_per_kg = models.FloatField(validators=[MinValueValidator(0.01)], help_text=_('Cost generated per Kg for product management and packaging'))
    is_foreign = models.BooleanField(default=False, help_text=_('Conditional for performance reporting to separate foreign and domestic markets; separation in the report of volume by mass and customer addresses'))
    is_mixable = models.BooleanField(default=False, verbose_name=_('Is mixable'), help_text=_('Conditional that does not allow mixing fruit with other markets'))
    label_language = models.CharField(max_length=100, choices=settings.LANGUAGES, default='es')
    address_label = CKEditor5Field(blank=True, null=True, verbose_name=_('Address on label with the packing house address'), help_text=_('Leave blank to use the default address defined in the organization'))
    is_enabled = models.BooleanField(default=True)
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Market')
        verbose_name_plural = _('Markets')
        unique_together = ('name', 'organization')


class KGCostMarket(models.Model):
    name = models.CharField(max_length=100)
    cost_per_kg = models.FloatField(validators=[MinValueValidator(0.01)])
    is_enabled = models.BooleanField(default=False)
    market = models.ForeignKey(Market, verbose_name=_('Market'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('KG Cost Market')
        verbose_name_plural = _('KG Cost Markets')
        unique_together = ('name', 'market')


class ProductQualityKind(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Product Quality Kind')
        verbose_name_plural = _('Product Quality Kinds')
        unique_together = ('name', 'organization')


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        unique_together = ('name', 'organization')


class ProductVariety(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.product.name} : {self.name}"

    class Meta:
        verbose_name = _('Product Variety')
        verbose_name_plural = _('Product Varieties')
        unique_together = ('name', 'product')


class ProductVarietyHarvestKind(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Product Variety Harvest Kind')
        verbose_name_plural = _('Product Variety Harvest Kinds')
        unique_together = ('name', 'organization')


class ProductVarietySizeKind(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Product Variety Size Kind')
        verbose_name_plural = _('Product Variety Size Kinds')
        unique_together = ('name', 'organization')


class ProductVarietySize(models.Model):
    market = models.ForeignKey(Market, verbose_name=_('Market'), on_delete=models.PROTECT)
    quality_kind = models.ForeignKey(ProductQualityKind, verbose_name=_('Product Quality Kind'), on_delete=models.PROTECT)
    name = models.CharField(max_length=160, verbose_name=_('Size Name'))
    # apeam... TODO: generalizar esto para que no sea solo apeam
    harvest_kind = models.ForeignKey(ProductVarietyHarvestKind, verbose_name=_('Product Variety Harvest Kind'), on_delete=models.PROTECT)
    description = models.CharField(max_length=200, verbose_name=_('Description'))
    # product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.PROTECT)
    variety = models.ForeignKey(ProductVariety, verbose_name=_('Product Variety'), on_delete=models.PROTECT)

    size_kind = models.ForeignKey(ProductVarietySizeKind, verbose_name=_('Product Variety Size Kind'), on_delete=models.PROTECT)
    requires_corner_protector = models.BooleanField(default=False, verbose_name=_('Requires Corner Protector'))
    is_enabled = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.variety.product.name} : {self.variety.name} : {self.name}"

    class Meta:
        verbose_name = _('Product Variety Size')
        verbose_name_plural = _('Product Variety Sizes')
        unique_together = ('name', 'variety')
        ordering = ['order']


# Proveedores de fruta:

class Bank(models.Model):
    name = models.CharField(max_length=120)
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Bank')
        verbose_name_plural = _('Banks')
        unique_together = ('name', 'organization')
        ordering = ('name',)


class ProductProvider(models.Model):
    name = models.CharField(max_length=255)
    state = models.ForeignKey(Region, on_delete=models.PROTECT)
    city = models.ForeignKey(City, on_delete=models.PROTECT)
    neighborhood = models.CharField(max_length=200)
    postal_code = models.CharField(max_length=10)
    address = models.CharField(max_length=255)
    external_number = models.CharField(max_length=20)
    internal_number = models.CharField(max_length=20)
    tax_id = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    bank_account_number = models.CharField(max_length=20)
    bank = models.ForeignKey(Bank, on_delete=models.PROTECT)
    is_enabled = models.BooleanField(default=False)
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Product Provider')
        verbose_name_plural = _('Product Providers')
        unique_together = ('name', 'organization')
        ordering = ('name',)


class ProductProviderBenefactor(models.Model):
    name = models.CharField(max_length=255)
    bank_account_number = models.CharField(max_length=20)
    bank = models.ForeignKey(Bank, on_delete=models.PROTECT)
    product_provider = models.ForeignKey(ProductProvider, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Product Provider Benefactor')
        verbose_name_plural = _('Product Provider Benefactors')
        unique_together = ('name', 'product_provider')
        ordering = ('name',)


# Productores


class ProductProducer(models.Model):
    name = models.CharField(max_length=255)
    state = models.ForeignKey(Region, on_delete=models.PROTECT)
    city = models.ForeignKey(City, on_delete=models.PROTECT)
    neighborhood = models.CharField(max_length=200)
    postal_code = models.CharField(max_length=10)
    address = models.CharField(max_length=255)
    external_number = models.CharField(max_length=20)
    internal_number = models.CharField(max_length=20)
    tax_id = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    product_provider = models.ForeignKey(ProductProvider, on_delete=models.PROTECT)
    bank_account_number = models.CharField(max_length=20)
    bank = models.ForeignKey(Bank, on_delete=models.PROTECT)
    is_enabled = models.BooleanField(default=False)
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Product Producer')
        verbose_name_plural = _('Product Producers')
        unique_together = ('name', 'organization')
        ordering = ('name',)


class ProductProducerBenefactor(models.Model):
    name = models.CharField(max_length=255)
    bank_account_number = models.CharField(max_length=20)
    bank = models.ForeignKey(Bank, on_delete=models.PROTECT)
    product_producer = models.ForeignKey(ProductProducer, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Product Producer Benefactor')
        verbose_name_plural = _('Product Producer Benefactors')
        unique_together = ('name', 'product_producer')
        ordering = ('name',)


class PaymentKind(models.Model):
    name = models.CharField(max_length=120)
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Payment Kind')
        verbose_name_plural = _('Payment Kinds')
        unique_together = ('name', 'organization')
        ordering = ('name',)


class Client(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Full name'))
    category = models.ForeignKey(LegalEntityCategory, verbose_name=_('Legal Entity Category'), on_delete=models.PROTECT)
    tax_id = models.CharField(max_length=30, verbose_name=_('Tax ID'))
    market = models.ForeignKey(Market, on_delete=models.PROTECT)
    country = models.ForeignKey(Country, verbose_name=_('Country'), default=158, on_delete=models.PROTECT, related_name='legal_entities')
    postal_code = models.CharField(max_length=10, verbose_name=_('Postal code'))
    state = models.CharField(max_length=255, verbose_name=_('State'))
    city = models.CharField(max_length=255, verbose_name=_('City'))
    district = models.CharField(max_length=255, verbose_name=_('District'), null=True, blank=True)
    neighborhood = models.CharField(max_length=255, verbose_name=_('Neighborhood'), null=True, blank=True)
    street = models.CharField(max_length=255, verbose_name=_('Street'), null=True, blank=True)
    ext_number = models.CharField(max_length=10, verbose_name=_('External number'), null=True, blank=True)
    int_number = models.CharField(max_length=10, verbose_name=_('Internal number'), null=True, blank=True)
    phone = models.CharField(max_length=15, verbose_name=_('Phone number'), null=True, blank=True)
    email = models.EmailField(verbose_name=_('Email'), null=True, blank=True)
    swift = models.CharField(max_length=20, verbose_name=_('SWIFT'), null=True, blank=True)
    aba = models.CharField(max_length=20, verbose_name=_('ABA'), null=True, blank=True)
    clabe = models.CharField(max_length=18, verbose_name=_('CLABE'), null=True, blank=True)
    payment_kind = models.ForeignKey(PaymentKind, verbose_name=_('Payment kind'), on_delete=models.PROTECT)
    credit_max_money_limit = models.FloatField(verbose_name=_('Credit max money limit'), null=True, blank=True)
    credit_max_days_limit = models.FloatField(verbose_name=_('Credit max days limit'), null=True, blank=True)

    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Client')
        verbose_name_plural = _('Clients')


class VehicleOwnership(models.Model):
    name = models.CharField(max_length=100)
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Ownership Status')
        verbose_name_plural = _('Ownership Statuses')
        unique_together = ('name', 'organization')


class VehicleKind(models.Model):
    name = models.CharField(max_length=100)
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Vehicle Kind')
        verbose_name_plural = _('Vehicle Kinds')
        unique_together = ('name', 'organization')


class VehicleFuel(models.Model):
    name = models.CharField(max_length=100)
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Fuel Kind')
        verbose_name_plural = _('Fuel Kinds')
        unique_together = ('name', 'organization')


class Vehicle(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    model = models.CharField(max_length=4, verbose_name=_('Model'), choices=vehicle_year_choices(), validators=[vehicle_validate_year])
    license_plate = models.CharField(max_length=15, verbose_name=_('License plate'))
    serial_number = models.CharField(max_length=100, verbose_name=_('Serial number'))
    color = models.CharField(max_length=50, verbose_name=_('Color'),)
    ownership = models.ForeignKey(VehicleOwnership, verbose_name=_('Ownership Status'), on_delete=models.PROTECT)
    fuel = models.ForeignKey(VehicleFuel, verbose_name=_('Fuel Name'), on_delete=models.PROTECT)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enable'),)
    comments = models.CharField(max_length=250, verbose_name=_('Comments'), blank=True, null=True, )
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Vehicle')
        verbose_name_plural = _('Vehicles')
        constraints = [
            models.UniqueConstraint(fields=['license_plate', 'organization'], name='unique_license_plate_org'),
            models.UniqueConstraint(fields=['serial_number', 'organization'], name='unique_serial_number_org')
        ]


class Collector(models.Model):
    zone = models.CharField(max_length=200, verbose_name=_('Zone'))
    first_name = models.CharField(max_length=255, verbose_name=_('First name'))
    last_name = models.CharField(max_length=255, verbose_name=_('Last name'))
    population_registry_code = models.CharField(max_length=20, verbose_name=_('Population registry code'))
    tax_registry_code = models.CharField(max_length=20, verbose_name=_('Population registry code'))
    social_number_code = models.CharField(max_length=20, verbose_name=_('Social number code'))
    birthday = models.DateField()
    sex = models.CharField(max_length=1, choices=(('', _('Sex')), ('male', _('Male'), ('female', _('Female')))))
    country = models.ForeignKey(Country, verbose_name=_('Country'), default=158, on_delete=models.PROTECT, related_name='legal_entities')
    state = models.CharField(max_length=255, verbose_name=_('State'))
    city = models.CharField(max_length=255, verbose_name=_('City'))
    district = models.CharField(max_length=255, verbose_name=_('District'), null=True, blank=True)
    neighborhood = models.CharField(max_length=255, verbose_name=_('Neighborhood'), null=True, blank=True)
    street = models.CharField(max_length=255, verbose_name=_('Street'), null=True, blank=True)
    ext_number = models.CharField(max_length=10, verbose_name=_('External number'), null=True, blank=True)
    int_number = models.CharField(max_length=10, verbose_name=_('Internal number'), null=True, blank=True)
    phone = models.CharField(max_length=15, verbose_name=_('Phone number'), null=True, blank=True)
    email = models.EmailField(verbose_name=_('Email'), null=True, blank=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT)
    is_enabled = models.BooleanField(default=True)
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = _('Collector')
        verbose_name_plural = _('Collectors')
