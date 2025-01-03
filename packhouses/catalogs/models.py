from django.db import models
from common.mixins import (CleanKindAndOrganizationMixin, CleanNameAndOrganizationMixin, CleanProductMixin,
                           CleanNameOrAliasAndOrganizationMixin, CleanNameAndMarketMixin, CleanNameAndProductMixin,
                           CleanNameAndProductProviderMixin, CleanNameAndProductProducerMixin,
                           CleanProductVarietyMixin,
                           CleanNameAndVarietyAndMarketAndVolumeKindMixin, CleanNameAndMaquiladoraMixin)
from organizations.models import Organization
from cities_light.models import City, Country, Region, SubRegion
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django_ckeditor_5.fields import CKEditor5Field
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from common.billing.models import TaxRegime, LegalEntityCategory
from .utils import vehicle_year_choices, vehicle_validate_year, get_type_choices, get_payment_choices, \
    vehicle_scope_choices
from django.core.exceptions import ValidationError
from common.base.models import ProductKind
from packhouses.packhouse_settings.models import (ProductSizeKind, ProductMassVolumeKind, Bank, VehicleOwnershipKind,
                                                  PaymentKind, VehicleFuelKind, VehicleKind, VehicleBrand,
                                                  OrchardProductClassificationKind, OrchardCertificationVerifier,
                                                  OrchardCertificationKind, SupplyKind, SupplyPresentationKind)
from django.db.models import Max, Min
from django.db.models import Q, F


# Create your models here.


# Markets

class Market(CleanNameOrAliasAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    alias = models.CharField(max_length=20, verbose_name=_('Alias'))
    countries = models.ManyToManyField(Country, verbose_name=_('Countries'))
    management_cost_per_kg = models.FloatField(verbose_name=_('Management cost per Kg'),
                                               validators=[MinValueValidator(0.01)], help_text=_(
            'Cost generated per Kg for product management and packaging'))
    is_foreign = models.BooleanField(default=False, verbose_name=_('Is foreign'), help_text=_(
        'Conditional for performance reporting to separate foreign and domestic markets; separation in the report of volume by mass and customer addresses'))
    is_mixable = models.BooleanField(default=True, verbose_name=_('Is mixable'),
                                     help_text=_('Conditional that does not allow mixing fruit with other markets'))
    label_language = models.CharField(max_length=20, verbose_name=_('Label language'), choices=settings.LANGUAGES,
                                      default='es')
    address_label = CKEditor5Field(blank=True, null=True, verbose_name=_('Address of packaging house to show in label'),
                                   help_text=_('Leave blank to keep the default address defined in the organization'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Market')
        verbose_name_plural = _('Markets')
        ordering = ('organization', 'name')
        constraints = [
            models.UniqueConstraint(fields=['name', 'organization'], name='market_unique_name_organization'),
            models.UniqueConstraint(fields=['alias', 'organization'], name='market_unique_alias_organization')
        ]


class KGCostMarket(CleanNameAndMarketMixin, models.Model):
    name = models.CharField(max_length=120, verbose_name=_('Name'))
    cost_per_kg = models.FloatField(validators=[MinValueValidator(0.01)], verbose_name=_('Cost per Kg'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    market = models.ForeignKey(Market, verbose_name=_('Market'), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Cost per Kg on Market')
        verbose_name_plural = _('Costs per Kg on Market')
        ordering = ('market', 'name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'market'], name='kgcostmarket_unique_name_market'),
        ]


class MarketClass(CleanNameAndMarketMixin, models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    market = models.ForeignKey(Market, verbose_name=_('Market'), on_delete=models.CASCADE)

    @receiver(post_save, sender=Market)
    def create_market_classes(sender, instance, created, **kwargs):
        if created:
            if not MarketClass.objects.filter(market=instance).exists():
                MarketClass.objects.bulk_create([
                    MarketClass(name='A', market=instance),
                    MarketClass(name='B', market=instance),
                    MarketClass(name='C', market=instance),
                ])

    class Meta:
        verbose_name = _('Market class')
        verbose_name_plural = _('Market classes')
        ordering = ('market', 'name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'market'], name='marketclass_unique_name_market'),
        ]


class MarketStandardProductSize(models.Model):
    # En caso de que se necesite poner "apeam" o algo similar, ver la posibilidad de ponerlo en el Market como atributo
    # a modo de autoridad en la materia
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    code = models.CharField(max_length=20, verbose_name=_('Code'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    market = models.ForeignKey(Market, verbose_name=_('Market'), on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0, verbose_name=_('Order'))

    def __str__(self):
        return f"{self.name}"

    def clean(self):
        errors = {}

        try:
            super().clean()
        except ValidationError as e:
            errors = e.message_dict

        if self.market_id:
            if self.__class__.objects.filter(name=self.name, market=self.market).exclude(pk=self.pk).exists():
                errors['name'] = _('Must be unique, it already exists.')

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('Market standard product size')
        verbose_name_plural = _('Market standard product sizes')
        ordering = ('order', 'name')
        constraints = [
            models.UniqueConstraint(fields=['name', 'market'], name='marketstandardproductsize_unique_name_market'),
        ]


# /Markets

# Products

class Product(CleanNameAndOrganizationMixin, models.Model):
    kind = models.ForeignKey(ProductKind, verbose_name=_('Product kind'), on_delete=models.PROTECT)
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    description = models.CharField(blank=True, null=True, max_length=255, verbose_name=_('Description'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ('organization', 'kind', 'name')
        constraints = [
            models.UniqueConstraint(fields=['name', 'organization'], name='product_unique_name_organization'),
        ]


class ProductVariety(CleanNameAndProductMixin, models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Variety name'))
    description = models.CharField(blank=True, null=True, max_length=255, verbose_name=_('Description'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Product variety')
        verbose_name_plural = _('Product varieties')
        ordering = ('product', 'name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'product'], name='product_unique_name_product'),
        ]


class ProductHarvestSizeKind(CleanProductMixin, models.Model):
    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.PROTECT)
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    order = models.IntegerField(default=0, verbose_name=_('Order'))

    class Meta:
        verbose_name = _('Product harvest size kind')
        verbose_name_plural = _('Product harvest size kinds')
        ordering = ('order', '-name')
        constraints = [
            models.UniqueConstraint(fields=['name', 'product'],
                                    name='productharvestsizekind_unique_name_product'),
        ]


class ProductVarietySize(CleanNameAndVarietyAndMarketAndVolumeKindMixin, CleanProductVarietyMixin, models.Model):
    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.PROTECT)
    product_variety = models.ForeignKey(ProductVariety, verbose_name=_('Product variety'), on_delete=models.PROTECT)
    market = models.ForeignKey(Market, verbose_name=_('Market'), on_delete=models.PROTECT)
    market_standard_product_size = models.ForeignKey(MarketStandardProductSize,
                                                     verbose_name=_('Market standard product size'),
                                                     help_text=_(
                                                         'Choose a Standard Product Size per Market (optional), it will put its name in the size name field.'),
                                                     on_delete=models.PROTECT, null=True, blank=True)
    name = models.CharField(max_length=160, verbose_name=_('Size name'))
    alias = models.CharField(max_length=20, verbose_name=_('Alias'))
    description = models.CharField(blank=True, null=True, max_length=255, verbose_name=_('Description'))
    product_harvest_size_kind = models.ForeignKey(ProductHarvestSizeKind,
                                                  verbose_name=_('Product harvest size kind'),
                                                  on_delete=models.PROTECT)
    product_size_kind = models.ForeignKey(ProductSizeKind, verbose_name=_('Size kind'),
                                          on_delete=models.PROTECT)  # Normal, roña, etc
    product_mass_volume_kind = models.ForeignKey(ProductMassVolumeKind, verbose_name=_('Mass volume kind'),
                                                 on_delete=models.PROTECT,
                                                 help_text=_(
                                                     'To separate sizes by product kind in the mass volume report'))  # Estandar, enmallado, orgánico...
    requires_corner_protector = models.BooleanField(default=False, verbose_name=_('Requires corner protector'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    order = models.PositiveIntegerField(default=0,
                                        verbose_name=_('Order'))  # TODO: implementar ordenamiento con drag and drop

    @property
    def product_name(self):
        return self.product_variety.product.name if self.product_variety and self.product_variety.product else None

    def __str__(self):
        return f"{self.product_variety.product.name}: {self.product_variety.name} ({self.name})"

    class Meta:
        verbose_name = _('Product variety size')
        verbose_name_plural = _('Product variety sizes')
        ordering = ['product_variety', 'order']
        constraints = [
            models.UniqueConstraint(fields=['name', 'product', 'product_variety', 'market', ],
                                    name='productvarietysize_unique_name_product_product_variety_market'),
        ]


# /Products

# Proveedores de fruta:

class ProductProvider(CleanNameOrAliasAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Full name'))
    alias = models.CharField(max_length=20, verbose_name=_('Alias'))
    state = models.ForeignKey(Region, verbose_name=_('State'), on_delete=models.PROTECT)
    city = models.ForeignKey(City, verbose_name=_('City'), on_delete=models.PROTECT)
    district = models.CharField(max_length=255, verbose_name=_('District'))
    neighborhood = models.CharField(max_length=255, verbose_name=_('Neighborhood'))
    postal_code = models.CharField(max_length=10, verbose_name=_('Postal code'))
    address = models.CharField(max_length=255, verbose_name=_('Address'))
    external_number = models.CharField(max_length=20, verbose_name=_('External number'))
    internal_number = models.CharField(max_length=20, verbose_name=_('Internal number'), null=True, blank=True)
    tax_id = models.CharField(max_length=100, verbose_name=_('Tax ID'))
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, verbose_name=_('Phone number'))
    bank_account_number = models.CharField(max_length=20, verbose_name=_('Bank account number'))
    bank = models.ForeignKey(Bank, on_delete=models.PROTECT, verbose_name=_('Bank'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Product provider')
        verbose_name_plural = _('Product providers')
        ordering = ('organization', 'name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'organization'], name='productprovider_unique_name_organization'),
            models.UniqueConstraint(fields=['alias', 'organization'], name='productprovider_unique_alias_organization')
        ]


class ProductProviderBenefactor(CleanNameAndProductProviderMixin, models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Full name'))
    bank_account_number = models.CharField(max_length=20, verbose_name=_('Bank account number'))
    bank = models.ForeignKey(Bank, on_delete=models.PROTECT, verbose_name=_('Bank'))
    provider = models.ForeignKey(ProductProvider, verbose_name=_('Product provider'), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Product Provider Benefactor')
        verbose_name_plural = _('Product Provider Benefactors')
        ordering = ('provider', 'name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'provider'], name='productproviderbenefactor_unique_name_provider'),
        ]


# Productores


class ProductProducer(CleanNameOrAliasAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Full name'))
    alias = models.CharField(max_length=20, verbose_name=_('Alias'))
    state = models.ForeignKey(Region, verbose_name=_('State'), on_delete=models.PROTECT)
    city = models.ForeignKey(City, verbose_name=_('City'), on_delete=models.PROTECT)
    district = models.CharField(max_length=255, verbose_name=_('District'), null=True, blank=True)
    postal_code = models.CharField(max_length=10, verbose_name=_('Postal code'))
    neighborhood = models.CharField(max_length=255, verbose_name=_('Neighborhood'))
    address = models.CharField(max_length=255, verbose_name=_('Address'))
    external_number = models.CharField(max_length=20, verbose_name=_('External number'))
    internal_number = models.CharField(max_length=20, verbose_name=_('Internal number'), null=True, blank=True)
    tax_id = models.CharField(max_length=100, verbose_name=_('Tax ID'))
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, verbose_name=_('Phone number'))
    product_provider = models.ForeignKey(ProductProvider, on_delete=models.PROTECT, verbose_name=_('Product provider'),
                                         null=True, blank=True)
    bank_account_number = models.CharField(max_length=20, verbose_name=_('Bank account number'))
    bank = models.ForeignKey(Bank, on_delete=models.PROTECT, verbose_name=_('Bank'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Product producer')
        verbose_name_plural = _('Product producers')
        ordering = ('organization', 'name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'organization'], name='productproducer_unique_name_organization'),
            models.UniqueConstraint(fields=['alias', 'organization'], name='productproducer_unique_alias_organization')
        ]


class ProductProducerBenefactor(CleanNameAndProductProducerMixin, models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    bank_account_number = models.CharField(max_length=20, verbose_name=_('Bank account number'))
    bank = models.ForeignKey(Bank, on_delete=models.PROTECT, verbose_name=_('Bank'))
    producer = models.ForeignKey(ProductProducer, on_delete=models.CASCADE, verbose_name=_('Product producer'))

    class Meta:
        verbose_name = _('Product producer benefactor')
        verbose_name_plural = _('Product producer benefactors')
        ordering = ('producer', 'name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'producer'], name='productproducerbenefactor_unique_name_producer'),
        ]


# Clientes


class Client(CleanNameAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Full name'))
    market = models.ForeignKey(Market, verbose_name=_('Market'), on_delete=models.PROTECT)
    country = models.ForeignKey(Country, verbose_name=_('Country'), on_delete=models.PROTECT, help_text=_(
        'Country of the client, must have a market selected to show the market countries.'))
    state = models.ForeignKey(Region, verbose_name=_('State'), on_delete=models.PROTECT)
    city = models.ForeignKey(City, verbose_name=_('City'), on_delete=models.PROTECT)
    district = models.CharField(max_length=255, verbose_name=_('District'), null=True, blank=True)
    postal_code = models.CharField(max_length=10, verbose_name=_('Postal code'))
    neighborhood = models.CharField(max_length=255, verbose_name=_('Neighborhood'))
    address = models.CharField(max_length=255, verbose_name=_('Address'))
    external_number = models.CharField(max_length=10, verbose_name=_('External number'))
    internal_number = models.CharField(max_length=10, verbose_name=_('Internal number'), null=True, blank=True)
    same_ship_address = models.BooleanField(default=False)
    legal_category = models.ForeignKey(LegalEntityCategory, verbose_name=_('Legal entity category'),
                                       null=True, blank=True,
                                       on_delete=models.PROTECT, help_text=_(
            'Legal category of the client, must have a country selected to show that country legal categories.'))
    tax_id = models.CharField(max_length=30, verbose_name=_('Client tax ID'))
    fda = models.CharField(max_length=20, verbose_name=_('FDA'), null=True, blank=True)
    swift = models.CharField(max_length=20, verbose_name=_('SWIFT'), null=True, blank=True)
    aba = models.CharField(max_length=20, verbose_name=_('ABA'), null=True, blank=True)
    clabe = models.CharField(max_length=18, verbose_name=_('CLABE'), null=True, blank=True)
    bank = models.ForeignKey(Bank, verbose_name=_('Bank'), on_delete=models.PROTECT, null=True, blank=True)
    payment_kind = models.ForeignKey(PaymentKind, verbose_name=_('Payment kind'), on_delete=models.PROTECT)
    max_money_credit_limit = models.FloatField(verbose_name=_('Max money credit limit'), null=True, blank=True)
    max_days_credit_limit = models.FloatField(verbose_name=_('Max days credit limit'), null=True, blank=True)
    contact_name = models.CharField(max_length=255, verbose_name=_('Contact person full name'))
    contact_email = models.EmailField()
    contact_phone_number = models.CharField(max_length=15, verbose_name=_('Phone number'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Client')
        verbose_name_plural = _('Clients')
        ordering = ('organization', 'market', 'name',)
        constraints = [
            models.UniqueConstraint(fields=('name', 'organization',), name='client_unique_name_organization'),
        ]


class ClientShipAddress(models.Model):
    country = models.ForeignKey(Country, verbose_name=_('Country'),
                                on_delete=models.PROTECT)  # TODO: verificar si se necesita país, pues ya el mercado tiene país
    state = models.ForeignKey(Region, verbose_name=_('State'), on_delete=models.PROTECT)
    city = models.ForeignKey(City, verbose_name=_('City'), on_delete=models.PROTECT)
    district = models.CharField(max_length=255, verbose_name=_('District'), null=True, blank=True)
    postal_code = models.CharField(max_length=10, verbose_name=_('Postal code'))
    neighborhood = models.CharField(max_length=255, verbose_name=_('Neighborhood'))
    address = models.CharField(max_length=255, verbose_name=_('Address'))
    external_number = models.CharField(max_length=10, verbose_name=_('External number'))
    internal_number = models.CharField(max_length=10, verbose_name=_('Internal number'), null=True, blank=True)
    client = models.OneToOneField(Client, on_delete=models.CASCADE, verbose_name=_('Client'))


# Vehículos

class HarvestingCrewProvider(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name / Legal name'))
    tax_id = models.CharField(max_length=100, verbose_name=_('Tax ID'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Harvesting Crew Provider')
        verbose_name_plural = _('Harvesting Crew Providers')
        constraints = [
            models.UniqueConstraint(fields=['name', 'organization'],
                                    name='harvesting_crew_provider_unique_name_organization'),
        ]


class Vehicle(CleanNameAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    kind = models.ForeignKey(VehicleKind, verbose_name=_('Vehicle Kind'), on_delete=models.PROTECT)
    brand = models.ForeignKey(VehicleBrand, verbose_name=_('Brand'), on_delete=models.PROTECT)
    model = models.CharField(max_length=4, verbose_name=_('Model'), choices=vehicle_year_choices(),
                             validators=[vehicle_validate_year])
    license_plate = models.CharField(max_length=15, verbose_name=_('License plate'))
    serial_number = models.CharField(max_length=100, verbose_name=_('Serial number'))
    color = models.CharField(max_length=50, verbose_name=_('Color'))
    ownership = models.ForeignKey(VehicleOwnershipKind, verbose_name=_('Ownership kind'), on_delete=models.PROTECT)
    scope = models.CharField(max_length=15, verbose_name=_('Scope'), choices=vehicle_scope_choices())
    fuel = models.ForeignKey(VehicleFuelKind, verbose_name=_('Fuel kind'), on_delete=models.PROTECT)
    comments = models.CharField(max_length=250, verbose_name=_('Comments'), blank=True, null=True)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    harvesting_crew_provider = models.ForeignKey(HarvestingCrewProvider, on_delete=models.CASCADE,
                                                 verbose_name=_('Harvesting Crew Provider'))

    class Meta:
        verbose_name = _('Vehicle')
        verbose_name_plural = _('Vehicles')
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'harvesting_crew_provider'],
                                    name='vehicle_unique_name_harvesting_crew_provider'),
            models.UniqueConstraint(fields=['license_plate', 'harvesting_crew_provider'],
                                    name='vehicle_unique_licenseplate_harvesting_crew_provider'),
            models.UniqueConstraint(fields=['serial_number', 'harvesting_crew_provider'],
                                    name='vehicle_unique_serialnumber_harvesting_crew_provider')
        ]


# Acopiadores


class Gatherer(CleanNameAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Full name'))
    zone = models.CharField(max_length=200, verbose_name=_('Zone'))
    tax_registry_code = models.CharField(max_length=20, verbose_name=_('Tax registry code'))
    population_registry_code = models.CharField(max_length=20, verbose_name=_('Population registry code'), null=True,
                                                blank=True)
    social_number_code = models.CharField(max_length=20, verbose_name=_('Social number code'), null=True, blank=True)
    state = models.ForeignKey(Region, verbose_name=_('State'), on_delete=models.PROTECT)
    city = models.ForeignKey(City, verbose_name=_('City'), on_delete=models.PROTECT)
    district = models.CharField(max_length=255, verbose_name=_('District'), null=True, blank=True)
    neighborhood = models.CharField(max_length=255, verbose_name=_('Neighborhood'), null=True, blank=True)
    postal_code = models.CharField(max_length=10, verbose_name=_('Postal code'), null=True, blank=True)
    address = models.CharField(max_length=255, verbose_name=_('Address'), null=True, blank=True)
    external_number = models.CharField(max_length=10, verbose_name=_('External number'), null=True, blank=True)
    internal_number = models.CharField(max_length=10, verbose_name=_('Internal number'), null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, verbose_name=_('Phone number'), null=True, blank=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Gatherer')
        verbose_name_plural = _('Gatherers')
        ordering = ('organization', 'name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'organization'], name='gatherer_unique_name_organization'),
        ]


class Maquiladora(CleanNameAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Full name'))
    zone = models.CharField(max_length=200, verbose_name=_('Zone'))
    tax_registry_code = models.CharField(max_length=20, verbose_name=_('Tax registry code'))
    population_registry_code = models.CharField(max_length=20, verbose_name=_('Population registry code'), null=True,
                                                blank=True)
    social_number_code = models.CharField(max_length=20, verbose_name=_('Social number code'), null=True, blank=True)
    state = models.ForeignKey(Region, verbose_name=_('State'), on_delete=models.PROTECT)
    city = models.ForeignKey(City, verbose_name=_('City'), on_delete=models.PROTECT)
    district = models.CharField(max_length=255, verbose_name=_('District'), null=True, blank=True)
    neighborhood = models.CharField(max_length=255, verbose_name=_('Neighborhood'), null=True, blank=True)
    postal_code = models.CharField(max_length=10, verbose_name=_('Postal code'), null=True, blank=True)
    address = models.CharField(max_length=255, verbose_name=_('Address'), null=True, blank=True)
    external_number = models.CharField(max_length=10, verbose_name=_('External number'), null=True, blank=True)
    internal_number = models.CharField(max_length=10, verbose_name=_('Internal number'), null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, verbose_name=_('Phone number'), null=True, blank=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, null=True, blank=True)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Maquiladora')
        verbose_name_plural = _('Maquiladoras')
        ordering = ('organization', 'name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'organization'], name='maquiladora_unique_name_organization'),
        ]


class MaquiladoraClient(CleanNameAndMaquiladoraMixin, models.Model):
    market = models.ForeignKey(Market, verbose_name=_('Market'), on_delete=models.PROTECT)
    country = models.ForeignKey(Country, verbose_name=_('Country'), default=158, on_delete=models.PROTECT)
    name = models.CharField(max_length=255, verbose_name=_('Full name'))
    legal_category = models.ForeignKey(LegalEntityCategory, verbose_name=_('Legal entity category'),
                                       null=True, blank=True,
                                       on_delete=models.PROTECT, help_text=_(
            'Legal category of the client, must have a country selected to show that country legal categories.'))
    tax_id = models.CharField(max_length=30, verbose_name=_('Tax ID'))
    state = models.ForeignKey(Region, verbose_name=_('State'), on_delete=models.PROTECT)
    city = models.ForeignKey(City, verbose_name=_('City'), on_delete=models.PROTECT)
    district = models.CharField(max_length=255, verbose_name=_('District'), null=True, blank=True)
    neighborhood = models.CharField(max_length=255, verbose_name=_('Neighborhood'), null=True, blank=True)
    postal_code = models.CharField(max_length=10, verbose_name=_('Postal code'), null=True, blank=True)
    address = models.CharField(max_length=255, verbose_name=_('Address'), null=True, blank=True)
    external_number = models.CharField(max_length=10, verbose_name=_('External number'), null=True, blank=True)
    internal_number = models.CharField(max_length=10, verbose_name=_('Internal number'), null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, verbose_name=_('Phone number'), null=True, blank=True)
    swift = models.CharField(max_length=20, verbose_name=_('SWIFT'), null=True, blank=True)
    aba = models.CharField(max_length=20, verbose_name=_('ABA'), null=True, blank=True)
    clabe = models.CharField(max_length=18, verbose_name=_('CLABE'), null=True, blank=True)
    bank = models.ForeignKey(Bank, verbose_name=_('Bank'), on_delete=models.PROTECT, null=True, blank=True)
    payment_kind = models.ForeignKey(PaymentKind, verbose_name=_('Payment kind'), on_delete=models.PROTECT)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    maquiladora = models.ForeignKey(Maquiladora, verbose_name=_('Maquiladora'), on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Maquiladora client')
        verbose_name_plural = _('Maquiladora clients')
        ordering = ('maquiladora', 'name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'maquiladora'], name='maquiladoraclient_unique_name_maquiladora'),
        ]


class Orchard(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    code = models.CharField(max_length=100, verbose_name=_('Registry code'))
    producer = models.ForeignKey(ProductProducer, verbose_name=_('Producer'), on_delete=models.PROTECT)
    safety_authority_registration_date = models.DateField(verbose_name=_('Safety authority registration date'))
    state = models.ForeignKey(Region, verbose_name=_('State'), on_delete=models.PROTECT)
    city = models.ForeignKey(City, verbose_name=_('City'), on_delete=models.PROTECT)
    district = models.CharField(max_length=255, verbose_name=_('District'), null=True, blank=True)
    ha = models.FloatField(verbose_name=_('Hectares'))
    product_classification_kind = models.ForeignKey(OrchardProductClassificationKind,
                                                    verbose_name=_('Product Classification'),
                                                    on_delete=models.PROTECT)
    phytosanitary_certificate = models.CharField(max_length=100, verbose_name=_('Phytosanitary certificate'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Orchard')
        verbose_name_plural = _('Orchards')
        ordering = ('organization', 'name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'organization'], name='orchard_unique_name_organization'),
            models.UniqueConstraint(fields=['code', 'organization'], name='orchard_unique_code_organization')
        ]


class OrchardCertification(models.Model):
    certification_kind = models.ForeignKey(OrchardCertificationKind, verbose_name=_('Orchard certification kind'),
                                           on_delete=models.PROTECT)
    certification_number = models.CharField(max_length=100, verbose_name=_('Certification number'))
    expiration_date = models.DateField(verbose_name=_('Expiration date'))
    verifier = models.ForeignKey(OrchardCertificationVerifier, verbose_name=_('Orchard certification verifier'),
                                 on_delete=models.PROTECT)
    extra_code = models.CharField(max_length=100, verbose_name=_('Extra code'), null=True, blank=True)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    orchard = models.ForeignKey(Orchard, verbose_name=_('Orchard'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.orchard.name} : {self.certification_kind.name}"

    class Meta:
        verbose_name = _('Orchard certification')
        verbose_name_plural = _('Orchard certifications')
        unique_together = ('orchard', 'certification_kind')
        ordering = ('orchard', 'certification_kind')


class CrewChief(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    harvesting_crew_provider = models.ForeignKey(HarvestingCrewProvider, verbose_name=_('Harvesting Crew Provider'),
                                                 on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Crew Chief')
        verbose_name_plural = _('Crew Chiefs')
        constraints = [
            models.UniqueConstraint(fields=['name', 'harvesting_crew_provider'],
                                    name='crew_chief_unique_name_harvesting_crew_provider'),
        ]


class HarvestingCrew(models.Model):
    ooid = models.IntegerField(verbose_name=_('OOID'), editable=False)
    harvesting_crew_provider = models.ForeignKey(HarvestingCrewProvider, verbose_name=_('Harvesting Crew Provider'),
                                                 on_delete=models.PROTECT)
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    certification_name = models.CharField(max_length=100, verbose_name=_('Certification Name'), blank=True, null=True)
    crew_chief = models.ForeignKey(CrewChief, verbose_name=_('Crew Chief'), on_delete=models.PROTECT)
    persons_number = models.IntegerField(verbose_name=_('Persons Number'),
                                         validators=[MinValueValidator(1), MaxValueValidator(9999)])
    comments = models.CharField(max_length=250, verbose_name=_('Comments'), blank=True, null=True)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Harvesting crew')
        verbose_name_plural = _('Harvesting crews')
        constraints = [
            models.UniqueConstraint(fields=['name', 'harvesting_crew_provider'],
                                    name='harversting_name_unique_harvesting_crew_provider'),
        ]


class HarvestingCrewBeneficiary(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    bank = models.ForeignKey(Bank, on_delete=models.PROTECT, verbose_name=_('Bank'))
    bank_account_number = models.CharField(max_length=18, verbose_name=_('Bank account number / CLABE'))
    harvesting_crew_provider = models.ForeignKey(HarvestingCrewProvider, on_delete=models.CASCADE,
                                                 verbose_name=_('Harvesting Crew Provider'))

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Harvesting crew beneficiary')
        verbose_name_plural = _('Harvesting crew beneficiaries')
        constraints = [
            models.UniqueConstraint(fields=['bank_account_number', 'harvesting_crew_provider'],
                                    name='bank_account_number_unique_harvesting_crew_provider'),
        ]


class HarvestingPaymentSetting(models.Model):
    type_harvest = models.CharField(max_length=20, choices=get_type_choices(), default='local',
                                    verbose_name=_('Type of harvest'))
    more_than_kg = models.FloatField(verbose_name=_('Kg of full truck'),
                                     help_text="From how many KG will the full truck payment be considered?",
                                     validators=[MinValueValidator(0.01)])

    pay_per_box_complete = models.FloatField(verbose_name=_('Pay per box (full truck)'),
                                             help_text="Payment per box in case of full truck",
                                             validators=[MinValueValidator(0.01)])
    pay_per_kg_complete = models.FloatField(verbose_name=_('Pay per kg (full truck)'),
                                            help_text="Payment per kg in case of full truck",
                                            validators=[MinValueValidator(0.01)])
    pay_per_day_complete = models.FloatField(verbose_name=_('Pay per day (full truck)'),
                                             help_text="Payment per day in case of full truck",
                                             validators=[MinValueValidator(0.01)])

    pay_per_box_incomplete = models.FloatField(verbose_name=_('Pay per box (incomplete truck)'),
                                               help_text="Payment per box in case of incomplete truck",
                                               validators=[MinValueValidator(0.01)])
    pay_per_kg_incomplete = models.FloatField(verbose_name=_('Pay per kg (incomplete truck)'),
                                              help_text="Payment per kg in case of incomplete truck",
                                              validators=[MinValueValidator(0.01)])
    pay_per_day_incomplete = models.FloatField(verbose_name=_('Pay per day (incomplete truck)'),
                                               help_text="Payment per day in case of incomplete truck",
                                               validators=[MinValueValidator(0.01)])

    type_payment_for_false_out = models.CharField(max_length=20, choices=get_payment_choices(), default='fixed_amount',
                                                  verbose_name=_('Type of Payment for false out'))
    amount_for_false_out = models.FloatField(verbose_name=_('Amount for false out'),
                                             validators=[MinValueValidator(0.01)])

    harvesting_crew = models.ForeignKey(HarvestingCrew, on_delete=models.CASCADE, verbose_name=_('Harvesting Crew'))

    def __str__(self):
        return f"{self.type_harvest}"

    class Meta:
        verbose_name = _('Payment Setting')
        verbose_name_plural = _('Payment Settings')
        constraints = [
            models.UniqueConstraint(fields=['type_harvest', 'harvesting_crew'],
                                    name='type_harvest_unique_harvesting_crew'),
        ]


#  Proveedores de insumos


class SupplyKindRelation(models.Model):
    from_kind = models.ForeignKey(SupplyKind, related_name='from_kind_relations', on_delete=models.CASCADE)
    to_kind = models.ForeignKey(SupplyKind, related_name='to_kind_relations', on_delete=models.CASCADE)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))

    def __str__(self):
        return f"{self.from_kind} -> {self.to_kind}"

    def clean(self):
        super().clean()
        if self.from_kind.organization != self.to_kind.organization:
            raise ValidationError(_('The organizations of from_kind and to_kind must be the same.'))

    class Meta:
        verbose_name = _('Supply kind relation')
        verbose_name_plural = _('Supply kind relations')


class Supply(CleanNameAndOrganizationMixin, models.Model):
    kind = models.ForeignKey(SupplyKind, verbose_name=_('Kind'), on_delete=models.PROTECT)
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    unit_quantity = models.PositiveIntegerField(verbose_name=_('Unit quantity'), help_text=_(
        'Quantity of units per unit kind to discunt when a supply is used'))
    presentation = models.ForeignKey(SupplyPresentationKind, verbose_name=_('Unit kind'), on_delete=models.PROTECT)
    minimum_stock_quantity = models.PositiveIntegerField(verbose_name=_('Minimum stock quantity'))
    maximum_stock_quantity = models.PositiveIntegerField(verbose_name=_('Maximum stock quantity'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.kind.name}: {self.name}"

    class Meta:
        verbose_name = _('Supply')
        verbose_name_plural = _('Supplies')
        ordering = ('organization', 'name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'organization'], name='supply_unique_name_organization'),
        ]


class SupplyProvider(CleanNameAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    tax_id = models.CharField(max_length=100, verbose_name=_('Tax ID'))
    state = models.ForeignKey(Region, verbose_name=_('State'), on_delete=models.PROTECT)
    city = models.ForeignKey(City, verbose_name=_('City'), on_delete=models.PROTECT)
    district = models.CharField(max_length=255, verbose_name=_('District'), null=True, blank=True)
    postal_code = models.CharField(max_length=10, verbose_name=_('Postal code'))
    neighborhood = models.CharField(max_length=255, verbose_name=_('Neighborhood'))
    address = models.CharField(max_length=255, verbose_name=_('Address'))
    external_number = models.CharField(max_length=20, verbose_name=_('External number'))
    internal_number = models.CharField(max_length=20, verbose_name=_('Internal number'), null=True, blank=True)
    payment_kind = models.ForeignKey(PaymentKind, verbose_name=_('Payment kind'), on_delete=models.PROTECT)
    credit_days = models.PositiveIntegerField(verbose_name=_('Credit days'))
    balance = models.FloatField(verbose_name=_('Balance'))
    contact_name = models.CharField(max_length=255, verbose_name=_('Contact person full name'))
    contact_email = models.EmailField()
    contact_phone_number = models.CharField(max_length=15, verbose_name=_('Phone number'))
    comments = models.CharField(max_length=250, verbose_name=_('Comments'), blank=True, null=True)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Supply provider')
        verbose_name_plural = _('Supply providers')
        ordering = ('organization', 'name')
        constraints = [
            models.UniqueConstraint(fields=['name', 'organization'], name='supplyprovider_unique_name_organization'),
        ]


class SupplyProviderSupply(models.Model):
    supply = models.ForeignKey(Supply, verbose_name=_('Supply'), on_delete=models.CASCADE)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    provider = models.ForeignKey(SupplyProvider, verbose_name=_('Provider'), on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.supply.name} ({self.provider.name})"

    class Meta:
        verbose_name = _('Supply from provider')
        verbose_name_plural = _('Supplies from providers')
        ordering = ('provider', 'supply')
        constraints = [
            models.UniqueConstraint(fields=['supply', 'provider'], name='supplyprovidersupply_unique_supply_provider'),
        ]


class SupplyProviderPaymentAccount(models.Model):
    bank = models.ForeignKey(Bank, on_delete=models.PROTECT, verbose_name=_('Bank'))
    bank_account_number = models.CharField(max_length=20, verbose_name=_('Bank account number'))
    interbank_account_number = models.CharField(max_length=20, verbose_name=_('Interbank account number'))
    provider = models.ForeignKey(SupplyProvider, on_delete=models.CASCADE, verbose_name=_('Provider'))

    def __str__(self):
        return f"{self.bank_account_number} ({self.provider.name})"

    class Meta:
        verbose_name = _('Supply provider payment account')
        verbose_name_plural = _('Supply provider payment accounts')
        constraints = [
            models.UniqueConstraint(fields=['bank', 'provider'],
                                    name='supplyproviderpaymentaccount_unique_bank_provider'),
        ]


# Presentaciones de mallas


class MeshBagKind(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Mesh Bag Kind')
        verbose_name_plural = _('Mesh Bag Kinds')
        unique_together = ('name', 'organization')


class MeshBagFilmKind(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Mesh bag film kind')
        verbose_name_plural = _('Mesh bag film kinds')
        unique_together = ('name', 'organization')


class MeshBag(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    market = models.ForeignKey(Market, verbose_name=_('Market'), on_delete=models.PROTECT)
    product_variety_size = models.ForeignKey(ProductVarietySize, verbose_name=_('Product variety size'),
                                             on_delete=models.PROTECT)
    mesh_bags_per_box = models.PositiveIntegerField(verbose_name=_('Mesh bags per box'))
    pieces_per_mesh_bag = models.PositiveIntegerField(verbose_name=_('Pieces per mesh bags'))
    mesh_bag_kind = models.ForeignKey(MeshBagKind, verbose_name=_('Mesh bag kind'), on_delete=models.PROTECT)
    mesh_bag_film_kind = models.ForeignKey(MeshBagFilmKind, verbose_name=_('Mesh bag film kind'),
                                           on_delete=models.PROTECT)
    mesh_bag_discount = models.FloatField(verbose_name=_('Mesh bag discount'))
    mesh_bag_film_discount = models.FloatField(verbose_name=_('Mesh bag film discount'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Mesh bag')
        verbose_name_plural = _('Mesh bags')
        unique_together = ('name', 'organization')


# Proveedores de servicios


class ServiceProvider(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    state = models.ForeignKey(Region, verbose_name=_('State'), on_delete=models.PROTECT)
    city = models.ForeignKey(City, verbose_name=_('City'), on_delete=models.PROTECT)
    district = models.CharField(max_length=255, verbose_name=_('District'), null=True, blank=True)
    neighborhood = models.CharField(max_length=255, verbose_name=_('Neighborhood'), null=True, blank=True)
    postal_code = models.CharField(max_length=10, verbose_name=_('Postal code'))
    address = models.CharField(max_length=255, verbose_name=_('Address'))
    external_number = models.CharField(max_length=20, verbose_name=_('External number'))
    internal_number = models.CharField(max_length=20, verbose_name=_('Internal number'))
    tax_id = models.CharField(max_length=100, verbose_name=_('Tax ID'))
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, verbose_name=_('Phone number'))
    bank_account_number = models.CharField(max_length=20, verbose_name=_('Bank account number'))
    bank = models.ForeignKey(Bank, on_delete=models.PROTECT, verbose_name=_('Bank'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Product provider')
        verbose_name_plural = _('Product providers')
        unique_together = ('name', 'organization')
        ordering = ('name',)


class ServiceProviderBenefactor(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Full name'))
    bank_account_number = models.CharField(max_length=20, verbose_name=_('Bank account number'))
    bank = models.ForeignKey(Bank, on_delete=models.PROTECT, verbose_name=_('Bank'))
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Service provider benefactor')
        verbose_name_plural = _('Service provider benefactors')
        unique_together = ('name', 'service_provider')
        ordering = ('name',)


class Service(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    service_provider = models.ForeignKey(ServiceProvider, verbose_name=_('Service provider'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Service')
        verbose_name_plural = _('Services')
        unique_together = ('name', 'service_provider')
        ordering = ('name',)


# Tipos de cajas

class AuthorityBoxKind(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Authority box kind')
        verbose_name_plural = _('Authority box kinds')
        unique_together = ('name', 'organization')


class BoxKind(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    kg_per_box = models.FloatField(verbose_name=_('Kg per box'))
    trays_per_box = models.PositiveIntegerField(verbose_name=_('Trays per box'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Box kind')
        verbose_name_plural = _('Box kinds')
        unique_together = ('name', 'organization')


# Básculas

class WeighingScale(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    number = models.CharField(max_length=20, verbose_name=_('Number'))
    state = models.ForeignKey(Region, verbose_name=_('State'), on_delete=models.PROTECT)
    city = models.ForeignKey(City, verbose_name=_('City'), on_delete=models.PROTECT)
    district = models.CharField(max_length=255, verbose_name=_('District'), null=True, blank=True)
    neighborhood = models.CharField(max_length=255, verbose_name=_('Neighborhood'), null=True, blank=True)
    postal_code = models.CharField(max_length=10, verbose_name=_('Postal code'))
    address = models.CharField(max_length=255, verbose_name=_('Address'))
    external_number = models.CharField(max_length=20, verbose_name=_('External number'))
    internal_number = models.CharField(max_length=20, verbose_name=_('Internal number'))
    comments = models.CharField(max_length=250, verbose_name=_('Comments'), blank=True, null=True)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Weighing scale')
        verbose_name_plural = _('Weighing scales')
        unique_together = ('name', 'organization')
        ordering = ('name',)


# Cámaras de frío


class ColdChamber(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.PROTECT)
    product_variety = models.ForeignKey(ProductVariety, verbose_name=_('Product variety'), on_delete=models.PROTECT)
    market = models.ForeignKey(Market, verbose_name=_('Market'), on_delete=models.PROTECT)
    pallet_capacity = models.PositiveIntegerField(verbose_name=_('Pallet capacity'))
    freshness_days_warning = models.PositiveIntegerField(verbose_name=_('Freshness days warning'))
    freshness_days_alert = models.PositiveIntegerField(verbose_name=_('Freshness days alert'))
    comments = models.CharField(max_length=250, verbose_name=_('Comments'), blank=True, null=True)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Cold chamber')
        verbose_name_plural = _('Cold chambers')
        unique_together = ('name', 'organization')
        ordering = ('name',)


# Pallets

class Pallet(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    alias = models.CharField(max_length=20, verbose_name=_('Alias'))
    boxes_quantity = models.PositiveIntegerField(verbose_name=_('Boxes quantity'))
    kg_amount = models.FloatField(verbose_name=_('Kg amount'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Pallet')
        verbose_name_plural = _('Pallets')
        unique_together = ('name', 'organization')


class PalletExpense(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    supply = models.ForeignKey(Supply, verbose_name=_('Supply'), on_delete=models.PROTECT, null=True, blank=True)
    quantity = models.PositiveIntegerField(verbose_name=_('Quantity'))
    unit_cost = models.FloatField(verbose_name=_('Unit cost'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    pallet = models.ForeignKey(Pallet, verbose_name=_('Pallet'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Pallet expense')
        verbose_name_plural = _('Pallet expenses')
        unique_together = ('name', 'pallet')


# configuración de productos

class ProductPackaging(models.Model):
    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.PROTECT)
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    alias = models.CharField(max_length=20, verbose_name=_('Alias'))
    boxes_quantity = models.PositiveIntegerField(verbose_name=_('Boxes quantity'))
    kg_amount = models.FloatField(verbose_name=_('Kg amount'))
    kg_tare = models.FloatField(verbose_name=_('Kg tare'))
    market = models.ForeignKey(Market, verbose_name=_('Market'), on_delete=models.PROTECT)
    box_kind = models.ForeignKey(BoxKind, verbose_name=_('Box kind'),
                                 on_delete=models.PROTECT)  # TODO: detallar tipos de caja por tipo de producto?
    product_variety = models.ForeignKey(ProductVariety, verbose_name=_('Product variety'), on_delete=models.PROTECT)
    product_variety_size = models.ForeignKey(ProductVarietySize, verbose_name=_('Product variety size'),
                                             on_delete=models.PROTECT)
    kg_per_box = models.FloatField(verbose_name=_('Kg per box'))
    supply = models.ForeignKey(Supply, verbose_name=_('Supply'), on_delete=models.PROTECT,
                               related_name='product_packaging_supplies')
    is_dark = models.BooleanField(default=False, verbose_name=_('Is dark'))
    provisional_cost = models.FloatField(verbose_name=_('provisional cost'))
    provisional_price = models.FloatField(verbose_name=_('provisional price'))
    market_class = models.ForeignKey(MarketClass, verbose_name=_('Market class'), on_delete=models.PROTECT)
    supply_tray = models.ForeignKey(Supply, verbose_name=_('Supply tray'), on_delete=models.PROTECT,
                                    related_name='product_packaging_supplies_trays')
    # TODO: agregar campo para tipo de malla, o no se que va aquí pero falta uno
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Product Packaging')
        verbose_name_plural = _('Product Packaging')
        unique_together = ('name', 'organization')


# Catálogos de exportación
class ExportingCompany(CleanNameAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name / Legal name'))
    country = models.ForeignKey(Country, verbose_name=_('Country'), on_delete=models.PROTECT)
    state = models.ForeignKey(Region, verbose_name=_('State'), on_delete=models.PROTECT)
    city = models.ForeignKey(City, verbose_name=_('City'), on_delete=models.PROTECT)
    district = models.CharField(max_length=255, verbose_name=_('District'), null=True, blank=True)
    postal_code = models.CharField(max_length=10, verbose_name=_('Postal code'))
    neighborhood = models.CharField(max_length=255, verbose_name=_('Neighborhood'))
    address = models.CharField(max_length=255, verbose_name=_('Address'))
    external_number = models.CharField(max_length=10, verbose_name=_('External number'))
    internal_number = models.CharField(max_length=10, verbose_name=_('Internal number'), null=True, blank=True)
    legal_category = models.ForeignKey(LegalEntityCategory, verbose_name=_('Legal entity category'),
                                       null=True, blank=True,
                                       on_delete=models.PROTECT, help_text=_(
            'Legal category of the exporting company, must have a country selected to show that country legal categories.'))
    tax_id = models.CharField(max_length=30, verbose_name=_('Tax ID'))
    clabe = models.CharField(max_length=18, verbose_name=_('CLABE'), null=True, blank=True)
    bank = models.ForeignKey(Bank, verbose_name=_('Bank'), on_delete=models.PROTECT, null=True, blank=True)
    payment_kind = models.ForeignKey(PaymentKind, verbose_name=_('Payment kind'), on_delete=models.PROTECT)
    contact_name = models.CharField(max_length=255, verbose_name=_('Contact person full name'))
    contact_email = models.EmailField()
    contact_phone_number = models.CharField(max_length=15, verbose_name=_('Phone number'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Exporting Company')
        verbose_name_plural = _('Exporting Companies')
        constraints = [
            models.UniqueConstraint(fields=('name', 'organization',),
                                    name='exporting_company_unique_name_organization'),
        ]


class Transfer(CleanNameAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name / Legal name'))
    caat = models.CharField(max_length=100, verbose_name=_('CAAT'))
    scac = models.CharField(max_length=100, verbose_name=_('SCAC'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Transfer')
        verbose_name_plural = _('Transfers')
        unique_together = ('name', 'organization')


class LocalTransporter(CleanNameAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name / Legal name'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Local Transporter')
        verbose_name_plural = _('Local Transporters')
        unique_together = ('name', 'organization')


class BorderToDestinationTransporter(CleanNameAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name / Legal name'))
    tax_id = models.CharField(max_length=100, verbose_name=_('Tax ID'))
    caat = models.CharField(max_length=100, verbose_name=_('CAAT'))
    irs = models.CharField(max_length=100, verbose_name=_('IRS'))
    scac = models.CharField(max_length=100, verbose_name=_('SCAC'))
    us_custom_bond = models.CharField(max_length=100, verbose_name=_('US Custom Bond'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Border To Destination Transporter')
        verbose_name_plural = _('Border To Destination Transporters')
        unique_together = ('name', 'organization')


class CustomsBroker(CleanNameAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name / Legal name'))
    broker_number = models.CharField(max_length=100, verbose_name=_('Broker number'))
    country = models.ForeignKey(Country, verbose_name=_('Country'), on_delete=models.PROTECT)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Customs Broker')
        verbose_name_plural = _('Customs Brokers')
        unique_together = ('name', 'organization')


class Vessel(CleanNameAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name / Legal name'))
    vessel_number = models.CharField(max_length=100, verbose_name=_('Vessel number'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Vessel')
        verbose_name_plural = _('Vessels')
        unique_together = ('name', 'organization')


class Airline(CleanNameAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name / Legal name'))
    airline_number = models.CharField(max_length=100, verbose_name=_('Airline number'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Airline')
        verbose_name_plural = _('Airlines')
        unique_together = ('name', 'organization')


class InsuranceCompany(CleanNameAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name / Legal name'))
    insurance_number = models.CharField(max_length=100, verbose_name=_('Insurance company number'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Insurance Company')
        verbose_name_plural = _('Insurance Companies')
        unique_together = ('name', 'organization')


class Provider(CleanNameAndOrganizationMixin, models.Model):
    ### Identification fields
    name = models.CharField(max_length=255, verbose_name=_('Name'))

    ### Localization fields
    country = models.ForeignKey(Country, on_delete=models.PROTECT, verbose_name=_('Country'))
    state = models.ForeignKey(Region, on_delete=models.PROTECT, verbose_name=_('State'))
    city = models.ForeignKey(SubRegion, on_delete=models.PROTECT, verbose_name=_('City'))
    district = models.ForeignKey(City, on_delete=models.PROTECT, verbose_name=_('District'))

    postal_code = models.CharField(max_length=10, verbose_name=_('Postal code'))
    neighborhood = models.CharField(max_length=255, verbose_name=_('Neighborhood'))
    address = models.CharField(max_length=255, verbose_name=_('Address'))
    external_number = models.CharField(max_length=10, verbose_name=_('External number'))
    internal_number = models.CharField(max_length=10, blank=True, null=True, verbose_name=_('Internal number'))

    ### Legal fields
    tax_id = models.CharField(max_length=100, verbose_name=_('Tax ID'))

    ### Contact fields
    email = models.EmailField(max_length=255, verbose_name=_('Email'))
    phone_number = models.CharField(max_length=10, blank=True, null=True, verbose_name=_('Phone number'))

    ### Status fields
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))

    ### Organization fields
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"[PROVIDER]: {self.name}"

    class Meta:
        verbose_name = _('Provider')
        verbose_name_plural = _('Providers')
