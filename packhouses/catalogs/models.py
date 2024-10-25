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
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    management_cost_per_kg = models.FloatField(verbose_name=_('Management cost per Kg'), validators=[MinValueValidator(0.01)], help_text=_('Cost generated per Kg for product management and packaging'))
    is_foreign = models.BooleanField(default=False, verbose_name=_('Is foreign'), help_text=_('Conditional for performance reporting to separate foreign and domestic markets; separation in the report of volume by mass and customer addresses'))
    is_mixable = models.BooleanField(default=False, verbose_name=_('Is mixable'), help_text=_('Conditional that does not allow mixing fruit with other markets'))
    label_language = models.CharField(max_length=100, verbose_name=_('Label language'), choices=settings.LANGUAGES, default='es')
    address_label = CKEditor5Field(blank=True, null=True, verbose_name=_('Address on label with the packaging house address'), help_text=_('Leave blank to use the default address defined in the organization'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Market')
        verbose_name_plural = _('Markets')
        unique_together = ('name', 'organization')


class KGCostMarket(models.Model):
    name = models.CharField(max_length=120, verbose_name=_('Name'))
    cost_per_kg = models.FloatField(validators=[MinValueValidator(0.01)], verbose_name=_('Cost per Kg'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    market = models.ForeignKey(Market, verbose_name=_('Market'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('KG Cost Market')
        verbose_name_plural = _('KG Cost Markets')
        unique_together = ('name', 'market')


class MarketClass(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    market = models.ForeignKey(Market, verbose_name=_('Market'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Market Class')
        verbose_name_plural = _('Market Classes')
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
    name = models.CharField(max_length=160, verbose_name=_('Variety size name'))
    alias = models.CharField(max_length=20, verbose_name=_('Variety size alias'))
    # apeam... TODO: generalizar esto para que no sea solo apeam
    harvest_kind = models.ForeignKey(ProductVarietyHarvestKind, verbose_name=_('Product Variety Harvest Kind'), on_delete=models.PROTECT)
    description = models.CharField(max_length=200, verbose_name=_('Description'))
    # product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.PROTECT)
    variety = models.ForeignKey(ProductVariety, verbose_name=_('Product Variety'), on_delete=models.PROTECT)

    size_kind = models.ForeignKey(ProductVarietySizeKind, verbose_name=_('Product Variety Size Kind'), on_delete=models.PROTECT)
    requires_corner_protector = models.BooleanField(default=False, verbose_name=_('Requires Corner Protector'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
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
    state = models.ForeignKey(Region, verbose_name=_('State'), on_delete=models.PROTECT)
    city = models.ForeignKey(City, verbose_name=_('City'), on_delete=models.PROTECT)
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
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
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
    state = models.ForeignKey(Region, verbose_name=_('State'), on_delete=models.PROTECT)
    city = models.ForeignKey(City, verbose_name=_('City'), on_delete=models.PROTECT)
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
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
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
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'),)
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
    sex = models.CharField(max_length=1, choices=[('', _('Sex')), ('M', _('Male')), ('F', _('Female'))])
    country = models.ForeignKey(Country, verbose_name=_('Country'), default=158, on_delete=models.PROTECT)
    state = models.ForeignKey(Region, verbose_name=_('State'), on_delete=models.PROTECT)
    city = models.CharField(max_length=255, verbose_name=_('City'))
    district = models.CharField(max_length=255, verbose_name=_('District'), null=True, blank=True)
    neighborhood = models.CharField(max_length=255, verbose_name=_('Neighborhood'), null=True, blank=True)
    street = models.CharField(max_length=255, verbose_name=_('Street'), null=True, blank=True)
    ext_number = models.CharField(max_length=10, verbose_name=_('External number'), null=True, blank=True)
    int_number = models.CharField(max_length=10, verbose_name=_('Internal number'), null=True, blank=True)
    phone = models.CharField(max_length=15, verbose_name=_('Phone number'), null=True, blank=True)
    email = models.EmailField(verbose_name=_('Email'), null=True, blank=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = _('Collector')
        verbose_name_plural = _('Collectors')


class Client(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Full name'))
    category = models.ForeignKey(LegalEntityCategory, verbose_name=_('Legal Entity Category'), on_delete=models.PROTECT)
    tax_id = models.CharField(max_length=30, verbose_name=_('Tax ID'))
    market = models.ForeignKey(Market, on_delete=models.PROTECT)
    country = models.ForeignKey(Country, verbose_name=_('Country'), default=158, on_delete=models.PROTECT)
    postal_code = models.CharField(max_length=10, verbose_name=_('Postal code'))
    state = models.ForeignKey(Region, verbose_name=_('State'), on_delete=models.PROTECT)
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
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Client')
        verbose_name_plural = _('Clients')


class Maquiladora(models.Model):
    zone = models.CharField(max_length=200, verbose_name=_('Zone'))
    first_name = models.CharField(max_length=255, verbose_name=_('First name'))
    last_name = models.CharField(max_length=255, verbose_name=_('Last name'))
    population_registry_code = models.CharField(max_length=20, verbose_name=_('Population registry code'))
    tax_registry_code = models.CharField(max_length=20, verbose_name=_('Population registry code'))
    social_number_code = models.CharField(max_length=20, verbose_name=_('Social number code'))
    birthday = models.DateField()
    sex = models.CharField(max_length=1, choices=[('', _('Sex')), ('M', _('Male')), ('F', _('Female'))])
    country = models.ForeignKey(Country, verbose_name=_('Country'), default=158, on_delete=models.PROTECT)
    state = models.ForeignKey(Region, verbose_name=_('State'), on_delete=models.PROTECT)
    city = models.CharField(max_length=255, verbose_name=_('City'))
    district = models.CharField(max_length=255, verbose_name=_('District'), null=True, blank=True)
    neighborhood = models.CharField(max_length=255, verbose_name=_('Neighborhood'), null=True, blank=True)
    street = models.CharField(max_length=255, verbose_name=_('Street'), null=True, blank=True)
    ext_number = models.CharField(max_length=10, verbose_name=_('External number'), null=True, blank=True)
    int_number = models.CharField(max_length=10, verbose_name=_('Internal number'), null=True, blank=True)
    phone = models.CharField(max_length=15, verbose_name=_('Phone number'), null=True, blank=True)
    email = models.EmailField(verbose_name=_('Email'), null=True, blank=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = _('Collector')
        verbose_name_plural = _('Collectors')


class MaquiladoraClient(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Full name'))
    category = models.ForeignKey(LegalEntityCategory, verbose_name=_('Legal Entity Category'), on_delete=models.PROTECT)
    tax_id = models.CharField(max_length=30, verbose_name=_('Tax ID'))
    market = models.ForeignKey(Market, on_delete=models.PROTECT)
    country = models.ForeignKey(Country, verbose_name=_('Country'), default=158, on_delete=models.PROTECT)
    postal_code = models.CharField(max_length=10, verbose_name=_('Postal code'))
    state = models.ForeignKey(Region, verbose_name=_('State'), on_delete=models.PROTECT)
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
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    maquiladora = models.ForeignKey(Maquiladora, verbose_name=_('Maquiladora'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Maquiladora Client')
        verbose_name_plural = _('Maquiladora Clients')


class OrchardProductClassification(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Product Classification')
        verbose_name_plural = _('Product Classifications')
        unique_together = ('name', 'organization')


class Orchard(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Orchard name'))
    producer = models.ForeignKey(ProductProducer, verbose_name=_('Producer'), on_delete=models.PROTECT)
    registration_date = models.DateField(verbose_name=_('Registration date'))
    forest_land_use_change = models.CharField(max_length=100, verbose_name=_('Forest land use change'))
    state = models.ForeignKey(Region, verbose_name=_('State'), on_delete=models.PROTECT)
    city = models.ForeignKey(City, verbose_name=_('City'), on_delete=models.PROTECT)
    district = models.CharField(max_length=255, verbose_name=_('District'), null=True, blank=True)
    ha = models.FloatField(verbose_name=_('Hectares'))
    product_classification = models.ForeignKey(OrchardProductClassification, verbose_name=_('Product Classification'), on_delete=models.PROTECT)
    phytosanitary_certificate = models.CharField(max_length=100, verbose_name=_('Phytosanitary certificate'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Orchard')
        verbose_name_plural = _('Orchards')
        unique_together = ('name', 'organization')
        ordering = ('name',)


class OrchardCertificationKind(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Orchard Certification Kind')
        verbose_name_plural = _('Orchard Certification Kinds')
        unique_together = ('name', 'organization')
        ordering = ('name',)


class OrchardCertificationVerifier(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Orchard Certification Verifier')
        verbose_name_plural = _('Orchard Certification Verifiers')
        unique_together = ('name', 'organization')
        ordering = ('name',)


class OrchardCertification(models.Model):
    certification_kind = models.ForeignKey(OrchardCertificationKind, verbose_name=_('Orchard Certification Kind'), on_delete=models.PROTECT)
    certification_number = models.CharField(max_length=100, verbose_name=_('Certification number'))
    expiration_date = models.DateField(verbose_name=_('Expiration date'))
    verifier = models.ForeignKey(OrchardCertificationVerifier, verbose_name=_('Verifier'), on_delete=models.PROTECT)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    orchard = models.ForeignKey(Orchard, verbose_name=_('Orchard'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.orchard.name} : {self.certification_kind.name}"

    class Meta:
        verbose_name = _('Orchard Certification')
        verbose_name_plural = _('Orchard Certifications')
        unique_together = ('orchard', 'certification_kind')
        ordering = ('orchard', 'certification_kind')


# Cuadrillas de cosecha

class HarvestCrew(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))

    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Harvest Crew')
        verbose_name_plural = _('Harvest Crews')
        unique_together = ('name', 'organization')
        ordering = ('name',)


#  Proveedores de insumos


class SupplyUnitKind(models.Model):
    name = models.CharField(max_length=100)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Supply Unit Kind')
        verbose_name_plural = _('Supply Unit Kinds')
        unique_together = ('name', 'organization')
        ordering = ('name',)


class SupplyKind(models.Model):
    name = models.CharField(max_length=100)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Supply Kind')
        verbose_name_plural = _('Supply Kinds')
        unique_together = ('name', 'organization')
        ordering = ('name',)


class SupplyKindRelation(models.Model):
    from_kind = models.ForeignKey(SupplyKind, related_name='from_kind_relations', on_delete=models.CASCADE)
    to_kind = models.ForeignKey(SupplyKind, related_name='to_kind_relations', on_delete=models.CASCADE)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))

    def __str__(self):
        return f"{self.from_kind} -> {self.to_kind}"

    class Meta:
        unique_together = ('from_kind', 'to_kind')
        verbose_name = _('Supply Kind Relation')
        verbose_name_plural = _('Supply Kind Relations')


class Supply(models.Model):
    name = models.CharField(max_length=255)
    unit_cost = models.FloatField()
    unit_price = models.FloatField()
    unit_quantity = models.PositiveIntegerField()
    unit_kind = models.ForeignKey(SupplyUnitKind, on_delete=models.PROTECT)
    minimum_stock_quantity = models.PositiveIntegerField()
    maximum_stock_quantity = models.PositiveIntegerField()
    kind = models.ForeignKey(SupplyKind, on_delete=models.PROTECT)
    is_tray = models.BooleanField(default=False)
    related_supply = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='related_supplies')
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Supply')
        verbose_name_plural = _('Supplies')
        unique_together = ('name', 'organization')
        ordering = ('name',)


class Supplier(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    tax_id = models.CharField(max_length=100)
    state = models.ForeignKey(Region, verbose_name=_('State'), on_delete=models.PROTECT)
    city = models.ForeignKey(City, verbose_name=_('City'), on_delete=models.PROTECT)
    neighborhood = models.CharField(max_length=200)
    postal_code = models.CharField(max_length=10)
    address = models.CharField(max_length=255)
    external_number = models.CharField(max_length=20)
    internal_number = models.CharField(max_length=20)
    payment_kind = models.ForeignKey(PaymentKind, on_delete=models.PROTECT)
    credit_days = models.PositiveIntegerField()
    balance = models.FloatField()
    supplies = models.ManyToManyField(Supply, verbose_name=_('Supplies'))
    observations = models.TextField(blank=True, null=True)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Supplier')
        verbose_name_plural = _('Suppliers')
        unique_together = ('name', 'organization')


# Presentaciones de mallas


class MeshBagKind(models.Model):
    name = models.CharField(max_length=100)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Mesh Bag Kind')
        verbose_name_plural = _('Mesh Bag Kinds')
        unique_together = ('name', 'organization')


class MeshBagFilmKind(models.Model):
    name = models.CharField(max_length=100)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Mesh Bag Film Kind')
        verbose_name_plural = _('Mesh Bag Film Kinds')
        unique_together = ('name', 'organization')


class MeshBag(models.Model):
    name = models.CharField(max_length=100)
    market = models.ForeignKey(Market, on_delete=models.PROTECT)
    product_variety_size = models.ForeignKey(ProductVarietySize, on_delete=models.PROTECT)
    meshbags_per_box = models.PositiveIntegerField()
    quantity_per_meshbags = models.PositiveIntegerField()
    meshbag_kind = models.ForeignKey(MeshBagKind, on_delete=models.PROTECT)
    meshbagfilm_kind = models.ForeignKey(MeshBagFilmKind, on_delete=models.PROTECT)
    meshbag_discount = models.FloatField()
    meshbagfilm_discount = models.FloatField()
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Mesh Bag')
        verbose_name_plural = _('Mesh Bags')
        unique_together = ('name', 'organization')


# Proveedores de servicios


class ServiceProvider(models.Model):
    name = models.CharField(max_length=255)
    state = models.ForeignKey(Region, verbose_name=_('State'), on_delete=models.PROTECT)
    city = models.ForeignKey(City, verbose_name=_('City'), on_delete=models.PROTECT)
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
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Product Provider')
        verbose_name_plural = _('Product Providers')
        unique_together = ('name', 'organization')
        ordering = ('name',)


class ServiceProviderBenefactor(models.Model):
    name = models.CharField(max_length=255)
    bank_account_number = models.CharField(max_length=20)
    bank = models.ForeignKey(Bank, on_delete=models.PROTECT)
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Service Provider Benefactor')
        verbose_name_plural = _('Service Provider Benefactors')
        unique_together = ('name', 'service_provider')
        ordering = ('name',)


class Service(models.Model):
    name = models.CharField(max_length=255)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Service')
        verbose_name_plural = _('Services')
        unique_together = ('name', 'service_provider')
        ordering = ('name',)


# Tipos de cajas

class AuthorityBoxKind(models.Model):
    name = models.CharField(max_length=100)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Authority Box Kind')
        verbose_name_plural = _('Authority Box Kinds')
        unique_together = ('name', 'organization')


class BoxKind(models.Model):
    name = models.CharField(max_length=100)
    kg_per_box = models.FloatField()
    trays_per_box = models.PositiveIntegerField()
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Box Kind')
        verbose_name_plural = _('Box Kinds')
        unique_together = ('name', 'organization')


# Básculas

class WeighingScale(models.Model):
    name = models.CharField(max_length=255)
    number = models.CharField(max_length=20)
    state = models.ForeignKey(Region, verbose_name=_('State'), on_delete=models.PROTECT)
    city = models.ForeignKey(City, verbose_name=_('City'), on_delete=models.PROTECT)
    neighborhood = models.CharField(max_length=200)
    postal_code = models.CharField(max_length=10)
    address = models.CharField(max_length=255)
    external_number = models.CharField(max_length=20)
    internal_number = models.CharField(max_length=20)
    observations = models.TextField(blank=True, null=True)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Weighing Scale')
        verbose_name_plural = _('Weighing Scales')
        unique_together = ('name', 'organization')
        ordering = ('name',)


# Cámaras de frío


class ColdChamber(models.Model):
    name = models.CharField(max_length=255)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    market = models.ForeignKey(Market, on_delete=models.PROTECT)
    pallets_capacity = models.PositiveIntegerField()
    freshness_days_warning = models.PositiveIntegerField()
    freshness_days_alert = models.PositiveIntegerField()
    observations = models.TextField(blank=True, null=True)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Cold Chamber')
        verbose_name_plural = _('Cold Chambers')
        unique_together = ('name', 'organization')
        ordering = ('name',)


# Pallets

class Pallet(models.Model):
    name = models.CharField(max_length=100)
    alias = models.CharField(max_length=20)
    boxes_quantity = models.PositiveIntegerField()
    kg_quantity = models.FloatField()
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Pallet')
        verbose_name_plural = _('Pallets')
        unique_together = ('name', 'organization')


class PalletExpense(models.Model):
    name = models.CharField(max_length=255)
    supply = models.ForeignKey(Supply, on_delete=models.PROTECT, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    unit_cost = models.FloatField()
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    pallet = models.ForeignKey(Pallet, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Pallet Expense')
        verbose_name_plural = _('Pallet Expenses')
        unique_together = ('name', 'pallet')


# configuración de productos

class ProductPackaging(models.Model):
    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    alias = models.CharField(max_length=20)
    boxes_quantity = models.PositiveIntegerField()
    kg_quantity = models.FloatField()
    kg_tare = models.FloatField()
    market = models.ForeignKey(Market, verbose_name=_('Market'), on_delete=models.PROTECT)
    box_kind = models.ForeignKey(BoxKind, verbose_name=_('Box Kind'), on_delete=models.PROTECT)  # TODO: detallar tipos de caja por tipo de producto?
    product_variety = models.ForeignKey(ProductVariety, verbose_name=_('Product Variety'), on_delete=models.PROTECT)
    product_variety_size = models.ForeignKey(ProductVarietySize, verbose_name=_('Product Variety Size'), on_delete=models.PROTECT)
    kg_per_box = models.FloatField()
    supply = models.ForeignKey(Supply, verbose_name=_('Supply'), on_delete=models.PROTECT, related_name='product_packaging_supplies')
    is_dark = models.BooleanField(default=False)
    provisional_cost = models.FloatField()
    provisional_price = models.FloatField()
    market_class = models.ForeignKey(MarketClass, verbose_name=_('Market Class'), on_delete=models.PROTECT)
    supply_tray = models.ForeignKey(Supply, verbose_name=_('Supply Tray'), on_delete=models.PROTECT, related_name='product_packaging_supplies_trays')
    # TODO: agregar campo para tipo de malla, o no se que va aquí pero falta uno
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Product Packaging')
        verbose_name_plural = _('Product Packagings')
        unique_together = ('name', 'organization')
