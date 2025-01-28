from django.db import models
from common.mixins import (CleanKindAndOrganizationMixin, CleanNameAndOrganizationMixin, CleanProductMixin,
                           CleanNameOrAliasAndOrganizationMixin, CleanNameAndMarketMixin, CleanNameAndProductMixin,
                           CleanNameAndProviderMixin, CleanNameAndCategoryAndOrganizationMixin,
                           CleanProductVarietyMixin, CleanNameAndAliasProductMixin,
                           CleanNameAndCodeAndOrganizationMixin,
                           CleanNameAndVarietyAndMarketAndVolumeKindMixin, CleanNameAndMaquiladoraMixin,
                           CleanNameAndServiceProviderAndOrganizationMixin)
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
    get_vehicle_category_choices, get_provider_categories_choices
from django.core.exceptions import ValidationError
from common.base.models import ProductKind, MarketProductSizeStandardSize
from packhouses.packhouse_settings.models import (Bank, VehicleOwnershipKind,
                                                  PaymentKind, VehicleFuelKind, VehicleKind, VehicleBrand,
                                                  AuthorityPackagingKind,
                                                  OrchardCertificationVerifier,
                                                  OrchardCertificationKind, SupplyKind)
from .settings import CLIENT_KIND_CHOICES, ORCHARD_PRODUCT_CLASSIFICATION_CHOICES
from packhouses.packhouse_settings.settings import SUPPLY_UNIT_KIND_CHOICES

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
            existing_classes = MarketClass.objects.filter(market=instance).values_list('name', flat=True)
            classes_to_create = [name for name in ['A', 'B', 'C'] if name not in existing_classes]
            if classes_to_create:
                MarketClass.objects.bulk_create([
                    MarketClass(name=name, market=instance) for name in classes_to_create
                ])

    class Meta:
        verbose_name = _('Market class')
        verbose_name_plural = _('Market classes')
        ordering = ('market', 'name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'market'], name='marketclass_unique_name_market'),
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


class ProductVariety(CleanNameAndAliasProductMixin, models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Variety name'))
    alias = models.CharField(max_length=20, verbose_name=_('Alias'))
    description = models.CharField(blank=True, null=True, max_length=255, verbose_name=_('Description'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Product variety')
        verbose_name_plural = _('Product varieties')
        ordering = ('product', 'name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'product'], name='product_unique_name_product'),
            models.UniqueConstraint(fields=['alias', 'product'], name='product_unique_alias_product'),
        ]


class ProductHarvestSizeKind(CleanProductMixin, models.Model):
    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.PROTECT)
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    sort_order = models.IntegerField(default=0, verbose_name=_('Sort order'))

    class Meta:
        verbose_name = _('Product harvest size kind')
        verbose_name_plural = _('Product harvest size kinds')
        ordering = ('product', 'sort_order', '-name')
        constraints = [
            models.UniqueConstraint(fields=['name', 'product'],
                                    name='productharvestsizekind_unique_name_product'),
        ]


class ProductSeasonKind(CleanNameAndProductMixin, models.Model):
    # Normal, roña, etc
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.PROTECT)
    sort_order = models.PositiveIntegerField(default=0, verbose_name=_('Sort order'))

    class Meta:
        verbose_name = _('Product season kind')
        verbose_name_plural = _('Product season kinds')
        ordering = ('product', 'sort_order',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'product'], name='productseasonkind_unique_name_product'),
        ]


class ProductMassVolumeKind(CleanNameAndProductMixin, models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    packaging_supply_kind = models.ForeignKey(SupplyKind, verbose_name=_('Packaging supply kind'), on_delete=models.PROTECT)
    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.PROTECT)
    sort_order = models.PositiveIntegerField(default=0, verbose_name=_('Sort order'))

    class Meta:
        verbose_name = _('Product mass volume kind')
        verbose_name_plural = _('Product mass volume kinds')
        ordering = ('product', 'sort_order',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'product'], name='productmassvolumekind_unique_name_product'),
        ]


class MarketProductSize(CleanNameAndAliasProductMixin, models.Model):
    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.PROTECT)
    varieties = models.ManyToManyField(ProductVariety, verbose_name=_('Varieties'), blank=False)
    market = models.ForeignKey(Market, verbose_name=_('Market'), on_delete=models.PROTECT)
    standard_size = models.ForeignKey(MarketProductSizeStandardSize, verbose_name=_('Standard size'), on_delete=models.PROTECT, null=True, blank=False)
    name = models.CharField(max_length=160, verbose_name=_('Size name'))
    alias = models.CharField(max_length=20, verbose_name=_('Alias'))
    description = models.CharField(max_length=255, verbose_name=_('Description'), blank=True, null=True)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    sort_order = models.PositiveIntegerField(default=0, verbose_name=_('Sort order'))

    def __str__(self):
        return f"{self.name} ({self.product.name})"

    class Meta:
        verbose_name = _('Market product size')
        verbose_name_plural = _('Market product sizes')
        ordering = ['sort_order']
        constraints = [
            models.UniqueConstraint(fields=['name', 'product'], name='marketproductsize_unique_name_product'),
            models.UniqueConstraint(fields=['alias', 'product'], name='marketproductsize_unique_alias_product'),
        ]

# /Products

# Vehicles

class Vehicle(CleanNameAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    category = models.CharField(max_length=15, verbose_name=_('Category'), choices=get_vehicle_category_choices())
    kind = models.ForeignKey(VehicleKind, verbose_name=_('Vehicle Kind'), on_delete=models.PROTECT)
    brand = models.ForeignKey(VehicleBrand, verbose_name=_('Brand'), on_delete=models.PROTECT)
    model = models.CharField(max_length=4, verbose_name=_('Model'), choices=vehicle_year_choices(),
                             validators=[vehicle_validate_year])
    license_plate = models.CharField(max_length=15, verbose_name=_('License plate'))
    serial_number = models.CharField(max_length=100, verbose_name=_('Serial number'))
    color = models.CharField(max_length=50, verbose_name=_('Color'))
    ownership = models.ForeignKey(VehicleOwnershipKind, verbose_name=_('Ownership kind'), on_delete=models.PROTECT)
    fuel = models.ForeignKey(VehicleFuelKind, verbose_name=_('Fuel kind'), on_delete=models.PROTECT)
    comments = models.CharField(max_length=250, verbose_name=_('Comments'), blank=True, null=True)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.license_plate} / {self.name}"

    class Meta:
        verbose_name = _('Vehicle')
        verbose_name_plural = _('Vehicles')
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(fields=['serial_number', 'organization'], name='vehicle_unique_serial_number_organization'),
        ]

# /Vehicles


# Providers

class Provider(CleanNameAndCategoryAndOrganizationMixin, models.Model):
    ### Identification fields
    name = models.CharField(max_length=255, verbose_name=_('Full name'))

    ### Provider Category
    category = models.CharField(max_length=255, choices=get_provider_categories_choices(), verbose_name=_('Category'))

    ### Reference to implied Provider (for producers)
    provider_provider = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Provider'))

    ### Reference to implied Provider (for harvesting crew providers)
    vehicle_provider = models.ManyToManyField(Vehicle, blank=True, verbose_name=_('Vehicle provider'))

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
    phone_number = models.CharField(max_length=20, verbose_name=_('Phone number'))

    ### Extra fields
    comments = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Comments'))

    ### Status fields
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))

    ### Organization fields
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Provider')
        verbose_name_plural = _('Providers')
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'category', 'organization'], name='provider_unique_name_organization'),
        ]


class ProviderBeneficiary(CleanNameAndProviderMixin, models.Model):
    ### Identification fields
    name = models.CharField(max_length=255, verbose_name=_("Name"))

    ### Bank details fields
    bank = models.ForeignKey(Bank, on_delete=models.PROTECT, verbose_name=_("Bank"))
    bank_account_number = models.CharField(max_length=25, verbose_name=_("Bank account number"))
    interbank_account_number = models.CharField(max_length=20, verbose_name=_('Interbank account number'))

    ### Reference to implied Provider
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, verbose_name=_("Provider"))

    class Meta:
        verbose_name = _("Provider's beneficiary")
        verbose_name_plural = _("Provider's beneficiaries")


class ProviderFinancialBalance(models.Model):
    ### Financial details
    balance_due = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('Balance due'))
    credit_days = models.PositiveIntegerField(default=0, verbose_name=_('Credit days'))

    ### Reference to implied Provider
    provider = models.OneToOneField(Provider, on_delete=models.CASCADE, verbose_name=_('Provider'))

    def __str__(self):
        return f"{self.provider.name}"

    class Meta:
        verbose_name = _('Provider financial balance')
        verbose_name_plural = _('Provider financial balances')

# /Providers


# Clientes


class Client(CleanNameAndCategoryAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Full name'))
    category = models.CharField(max_length=20, choices=CLIENT_KIND_CHOICES, verbose_name=_('Client category'))
    market = models.ForeignKey(Market, verbose_name=_('Market'), on_delete=models.PROTECT)
    country = models.ForeignKey(Country, verbose_name=_('Country'), on_delete=models.PROTECT, help_text=_(
        'Country of the client, must have a market selected to show the market countries.'))
    state = models.ForeignKey(Region, verbose_name=_('State'), on_delete=models.PROTECT)
    city = models.ForeignKey(SubRegion, verbose_name=_('City'), on_delete=models.PROTECT)
    district = models.ForeignKey(City, verbose_name=_('District'), on_delete=models.PROTECT, null=True, blank=True)
    postal_code = models.CharField(max_length=10, verbose_name=_('Postal code'))
    neighborhood = models.CharField(max_length=255, verbose_name=_('Neighborhood'))
    address = models.CharField(max_length=255, verbose_name=_('Address'))
    external_number = models.CharField(max_length=10, verbose_name=_('External number'))
    internal_number = models.CharField(max_length=10, verbose_name=_('Internal number'), null=True, blank=True)
    # same_ship_address = models.BooleanField(default=False)
    shipping_address = models.OneToOneField('catalogs.ClientShippingAddress',
                                        verbose_name=_('Shipping address'),
                                        help_text=_('Shipping address of the client, leave it blank if you want to use the client address for shipping, or select one if you want to use a different one.'),
                                        on_delete=models.PROTECT, null=True, blank=True, related_name='shipping_address_clients')
    legal_category = models.ForeignKey(LegalEntityCategory, verbose_name=_('Legal entity category'),
                                       null=True, blank=True,
                                       on_delete=models.PROTECT, help_text=_(
            'Legal category of the client, must have a country selected to show that country legal categories.'))
    tax_id = models.CharField(max_length=30, verbose_name=_('Client tax ID'))
    payment_kind = models.ForeignKey(PaymentKind, verbose_name=_('Payment kind'), on_delete=models.PROTECT)
    max_money_credit_limit = models.FloatField(verbose_name=_('Max money credit limit'), null=True, blank=True)
    max_days_credit_limit = models.FloatField(verbose_name=_('Max days credit limit'), null=True, blank=True)
    fda = models.CharField(max_length=20, verbose_name=_('FDA'), null=True, blank=True)
    swift = models.CharField(max_length=20, verbose_name=_('SWIFT'), null=True, blank=True)
    aba = models.CharField(max_length=20, verbose_name=_('ABA'), null=True, blank=True)
    clabe = models.CharField(max_length=18, verbose_name=_('CLABE'), null=True, blank=True)
    bank = models.ForeignKey(Bank, verbose_name=_('Bank'), on_delete=models.PROTECT, null=True, blank=True)
    contact_name = models.CharField(max_length=255, verbose_name=_('Contact person full name'))
    contact_email = models.EmailField()
    contact_phone_number = models.CharField(max_length=15, verbose_name=_('Contact phone number'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Client')
        verbose_name_plural = _('Clients')
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(fields=('name', 'category', 'organization',), name='client_unique_name_category_organization'),
        ]


class ClientShippingAddress(models.Model):
    address_name = models.CharField(max_length=255, verbose_name=_('Address name'))
    country = models.ForeignKey(Country, verbose_name=_('Country'),
                                on_delete=models.PROTECT)  # TODO: verificar si se necesita país, pues ya el mercado tiene país
    state = models.ForeignKey(Region, verbose_name=_('State'), on_delete=models.PROTECT)
    city = models.ForeignKey(SubRegion, verbose_name=_('City'), on_delete=models.PROTECT)
    district = models.ForeignKey(City, verbose_name=_('District'), on_delete=models.PROTECT, null=True, blank=True)
    postal_code = models.CharField(max_length=10, verbose_name=_('Postal code'))
    neighborhood = models.CharField(max_length=255, verbose_name=_('Neighborhood'))
    address = models.CharField(max_length=255, verbose_name=_('Address'))
    external_number = models.CharField(max_length=10, verbose_name=_('External number'))
    internal_number = models.CharField(max_length=10, verbose_name=_('Internal number'), null=True, blank=True)
    references = models.CharField(max_length=255, verbose_name=_('References'), null=True, blank=True)
    contact_name = models.CharField(max_length=255, verbose_name=_('Contact person full name'), null=True, blank=True)
    contact_phone_number = models.CharField(max_length=15, verbose_name=_('Phone number'), null=True, blank=True)
    comments = models.CharField(max_length=255, verbose_name=_('Comments'), null=True, blank=True)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name=_('Client'))

    def __str__(self):
        return f"{self.address_name}"

    class Meta:
        verbose_name = _('Client shipping address')
        verbose_name_plural = _('Client shipping addresses')
        ordering = ('client', 'address_name',)
        constraints = [
            models.UniqueConstraint(fields=('address_name', 'client',), name='clientshippingaddress_unique_address_name_client'),
        ]


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

# Acopiadores


class Gatherer(CleanNameAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Full name'))
    zone = models.CharField(max_length=200, verbose_name=_('Zone'))
    tax_registry_code = models.CharField(max_length=20, verbose_name=_('Tax registry code'))
    population_registry_code = models.CharField(max_length=20, verbose_name=_('Population registry code'), null=True,
                                                blank=True)
    social_number_code = models.CharField(max_length=20, verbose_name=_('Social number code'), null=True, blank=True)
    state = models.ForeignKey(Region, verbose_name=_('State'), on_delete=models.PROTECT)
    city = models.ForeignKey(SubRegion, verbose_name=_('City'), on_delete=models.PROTECT)
    district = models.ForeignKey(City, verbose_name=_('District'), on_delete=models.PROTECT, null=True, blank=True)
    postal_code = models.CharField(max_length=10, verbose_name=_('Postal code'))
    neighborhood = models.CharField(max_length=255, verbose_name=_('Neighborhood'))
    address = models.CharField(max_length=255, verbose_name=_('Address'))
    external_number = models.CharField(max_length=10, verbose_name=_('External number'))
    internal_number = models.CharField(max_length=10, verbose_name=_('Internal number'), null=True, blank=True)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, verbose_name=_('Phone number'), null=True, blank=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, help_text=_("Only shows the vehicles that belongs to 'packhouse' category"))
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
    tax_id = models.CharField(max_length=20, verbose_name=_('Tax ID'))
    # population_registry_code = models.CharField(max_length=20, verbose_name=_('Population registry code'), null=True, blank=True)
    # social_number_code = models.CharField(max_length=20, verbose_name=_('Social number code'), null=True, blank=True)
    state = models.ForeignKey(Region, verbose_name=_('State'), on_delete=models.PROTECT)
    city = models.ForeignKey(SubRegion, verbose_name=_('City'), on_delete=models.PROTECT)
    district = models.ForeignKey(City, verbose_name=_('District'), on_delete=models.PROTECT)
    neighborhood = models.CharField(max_length=255, verbose_name=_('Neighborhood'))
    postal_code = models.CharField(max_length=10, verbose_name=_('Postal code'))
    address = models.CharField(max_length=255, verbose_name=_('Address'))
    external_number = models.CharField(max_length=10, verbose_name=_('External number'))
    internal_number = models.CharField(max_length=10, verbose_name=_('Internal number'), null=True, blank=True)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15, verbose_name=_('Phone number'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)
    maquiladora_clients = models.ManyToManyField(Client, verbose_name=_('Maquiladora clients'), blank=False,
                                                 help_text=_('Clients associated with this maquiladora, it must be created before at Catalogs:Clients section.'))

    class Meta:
        verbose_name = _('Maquiladora')
        verbose_name_plural = _('Maquiladoras')
        ordering = ('organization', 'name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'organization'], name='maquiladora_unique_name_organization'),
        ]


class Orchard(CleanNameAndCodeAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    code = models.CharField(max_length=100, verbose_name=_('Registry code'))
    category = models.CharField(max_length=100, verbose_name=_('Product category'), choices=ORCHARD_PRODUCT_CLASSIFICATION_CHOICES)
    product = models.ManyToManyField(Product, verbose_name=_('Product'), blank=True,)
    producer = models.ForeignKey(Provider, verbose_name=_('Producer'), on_delete=models.PROTECT)
    safety_authority_registration_date = models.DateField(verbose_name=_('Safety authority registration date'))
    state = models.ForeignKey(Region, verbose_name=_('State'), on_delete=models.PROTECT)
    city = models.ForeignKey(SubRegion, verbose_name=_('City'), on_delete=models.PROTECT)
    district = models.ForeignKey(City, verbose_name=_('District'), on_delete=models.PROTECT)
    ha = models.FloatField(verbose_name=_('Hectares'))
    sanitary_certificate = models.CharField(max_length=100, verbose_name=_('Sanitary certificate'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.code} - {self.name}"

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
    orchard = models.ForeignKey(Orchard, verbose_name=_('Orchard'), on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.orchard.name} : {self.certification_kind.name}"

    class Meta:
        verbose_name = _('Orchard certification')
        verbose_name_plural = _('Orchard certifications')
        unique_together = ('orchard', 'certification_kind')
        ordering = ('orchard', 'certification_kind')


class CrewChief(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    provider = models.ForeignKey(Provider, verbose_name=_('Harvesting Crew Provider'), on_delete=models.PROTECT)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Crew Chief')
        verbose_name_plural = _('Crew Chiefs')
        constraints = [
            models.UniqueConstraint(fields=['name', 'provider'], name='crew_chief_unique_name_provider'),
        ]

class HarvestingCrew(models.Model):
    provider = models.ForeignKey(Provider, verbose_name=_('Harvesting Crew Provider'),
                                                 on_delete=models.PROTECT)
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    certification_name = models.CharField(max_length=100, verbose_name=_('Certification Name'), blank=True, null=True)
    crew_chief = models.ForeignKey(CrewChief, verbose_name=_('Crew Chief'), on_delete=models.PROTECT)
    persons_number = models.IntegerField(verbose_name=_('Persons Number'),
                                         validators=[MinValueValidator(1), MaxValueValidator(9999)])
    comments = models.CharField(max_length=250, verbose_name=_('Comments'), blank=True, null=True)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    def get_persons_range(self):
        return range(1, self.persons_number + 1)
    
    class Meta:
        verbose_name = _('Harvesting crew')
        verbose_name_plural = _('Harvesting crews')
        constraints = [
            models.UniqueConstraint(fields=['name', 'provider'],
                                    name='harversting_name_unique_provider'),
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

class SupplyPackage(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    supply = models.ForeignKey(Supply, verbose_name=_('Supply'), on_delete=models.PROTECT)
    quantity = models.FloatField(verbose_name=_('Quantity'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))

    def __str__(self):
        return f"{self.name} ({self.supply.name})"

    class Meta:
        verbose_name = _('Supply package')
        verbose_name_plural = _('Supply packages')
        ordering = ('supply', 'name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'supply'], name='supplypackage_unique_name_supply'),
        ]


class ProviderSupply(models.Model):
    supply = models.ForeignKey(Supply, verbose_name=_('Supply'), on_delete=models.PROTECT)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    provider = models.ForeignKey(Provider, verbose_name=_('Provider'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.supply.name} ({self.provider.name})"

    class Meta:
        verbose_name = _('Supply from provider')
        verbose_name_plural = _('Supplies from providers')
        ordering = ('provider', 'supply')
        constraints = [
            models.UniqueConstraint(fields=['supply', 'provider'], name='providersupply_unique_supply_provider'),
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
    product_variety_size = models.ForeignKey(MarketProductSize, verbose_name=_('Product variety size'),
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


class PackagingPresentation(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    packaging_supply_kind = models.ForeignKey(SupplyKind, verbose_name=_('Packaging supply kind'), on_delete=models.PROTECT)
    market = models.ForeignKey(Market, verbose_name=_('Market'), on_delete=models.PROTECT)
    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.PROTECT)
    product_variety = models.ForeignKey(ProductVariety, verbose_name=_('Product variety'), on_delete=models.PROTECT)
    product_variety_size = models.ForeignKey(MarketProductSize, verbose_name=_('Variety size'), on_delete=models.PROTECT)

    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Packaging presentation')
        verbose_name_plural = _('Packaging presentations')
        unique_together = ('name', 'organization')


# Proveedores de servicios


class Service(CleanNameAndServiceProviderAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    service_provider = models.ForeignKey(Provider, verbose_name=_('Provider'), on_delete=models.PROTECT)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Service')
        verbose_name_plural = _('Services')
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(fields=('name', 'service_provider', 'organization'),
                                    name='service_unique_name_service_provider_organization'),
        ]


# Tipos de empaques


class Packaging(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))

    ### Authority
    authority = models.ForeignKey(AuthorityPackagingKind, blank=True, null=True, on_delete=models.PROTECT)
    code = models.CharField(max_length=10, blank=True, null=True, verbose_name=_('Code'))

    ### Embalaje principal
    main_supply_kind = models.ForeignKey(SupplyKind, verbose_name=_('Main supply kind'), on_delete=models.PROTECT)
    main_supply = models.ForeignKey(Supply, verbose_name=_('Main supply'), on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(verbose_name=_('Quantity'))

    ### Máximo peso
    max_product_kg_per_package = models.FloatField(verbose_name=_('Max product Kg per package'))
    #avg_tare_kg_per_package = models.FloatField(verbose_name=_('Average tare Kg per package'))

    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Packaging')
        verbose_name_plural = _('Packaging')
        ordering = ('name', )
        constraints = [
            models.UniqueConstraint(fields=('name', 'organization'),
                                    name='packaging_unique_name_organization'),
        ]

class PackagingSupply(models.Model):
    packaging_kind = models.ForeignKey(Packaging, on_delete=models.PROTECT)
    supply_kind = models.ForeignKey(SupplyKind, verbose_name=_('Supply kind'), on_delete=models.PROTECT)
    supply = models.ForeignKey(Supply, verbose_name=_('Supply'), on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(verbose_name=_('Quantity'))

    class Meta:
        verbose_name = _('Packaging supply')
        verbose_name_plural = _('Packaging supplies')
        ordering = ('supply_kind', 'supply')
        #constraints = [
        #    models.UniqueConstraint(fields=('packaging_kind', 'supply_kind'),
        #                            name='insidesupply_unique_packagingkind_supplykind'),
        #]


class RelationPackaging(models.Model):
    outside = models.ForeignKey(Packaging, on_delete=models.PROTECT, related_name='outside')
    inside = models.ForeignKey(Packaging, on_delete=models.PROTECT, related_name='inside')
    quantity = models.PositiveIntegerField(verbose_name=_('Quantity'))

    class Meta:
        unique_together = ('outside', 'inside')


# Básculas

class WeighingScale(CleanNameAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    number = models.CharField(max_length=20, verbose_name=_('Number'), null=True, blank=True)
    state = models.ForeignKey(Region, verbose_name=_('State'), on_delete=models.PROTECT)
    city = models.ForeignKey(SubRegion, verbose_name=_('City'), on_delete=models.PROTECT)
    district = models.ForeignKey(City, verbose_name=_('District'), on_delete=models.PROTECT, null=True, blank=True)
    neighborhood = models.CharField(max_length=255, verbose_name=_('Neighborhood'))
    postal_code = models.CharField(max_length=10, verbose_name=_('Postal code'))
    address = models.CharField(max_length=255, verbose_name=_('Address'))
    external_number = models.CharField(max_length=20, verbose_name=_('External number'))
    internal_number = models.CharField(max_length=20, verbose_name=_('Internal number'), null=True, blank=True)
    comments = models.CharField(max_length=250, verbose_name=_('Comments'), blank=True, null=True)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Weighing Scale')
        verbose_name_plural = _('Weighing Scales')
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'organization'], name='weighing_scale_unique_name_organization'),
        ]


# Cámaras de frío


class ColdChamber(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    market = models.ForeignKey(Market, verbose_name=_('Market'), on_delete=models.PROTECT)
    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.PROTECT)
    product_variety = models.ForeignKey(ProductVariety, verbose_name=_('Product variety'), on_delete=models.PROTECT)
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
class PalletConfiguration(CleanNameOrAliasAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'), null=False, blank=False)
    alias = models.CharField(max_length=20, verbose_name=_('Alias'), null=False, blank=False)
    market = models.ForeignKey(Market, verbose_name=_('Market'), on_delete=models.PROTECT, null=False, blank=False)
    market_class = models.ForeignKey(MarketClass, verbose_name=_('Market class'), on_delete=models.PROTECT)
    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.PROTECT, null=False, blank=False)
    product_variety = models.ForeignKey(ProductVariety, verbose_name=_('Product Variety'), on_delete=models.PROTECT, null=False, blank=False)
    product_size = models.ForeignKey(MarketProductSize, verbose_name=_('Product Size'), on_delete=models.PROTECT, null=False, blank=False)
    maximum_boxes_per_pallet = models.PositiveIntegerField(verbose_name=_('Boxes quantity'), null=False, blank=False, help_text=_(
        "Maximum number of boxes per pallet"
    ))
    maximum_kg_per_pallet = models.FloatField(verbose_name=_('Kg amount'), null=False, blank=False, help_text=_(
        "Maximum Kg per pallet"
    ))
    kg_tare = models.FloatField(verbose_name=_('Kg tare'), null=True, blank=True)
    kg_per_box = models.FloatField(verbose_name=_('Kg per box'), null=False, blank=False)
    packaging_kind = models.ForeignKey(Packaging, verbose_name=_('Packaging kind'), on_delete=models.PROTECT)
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name=_('Creation date'))
    is_ripe = models.BooleanField(default=False, verbose_name=_('Is ripe'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Pallet Configuration')
        verbose_name_plural = _('Pallet Configuration')
        ordering = ('name','alias')
        constraints = [
            models.UniqueConstraint(fields=['name', 'organization'], name='pallet_configuration_unique_name_organization'),
            models.UniqueConstraint(fields=['alias', 'organization'], name='pallet_configuration_unique_alias_organization')
        ]

class PalletConfigurationSupplyExpense(models.Model):
    supply = models.ForeignKey(Supply, verbose_name=_('Supply'), on_delete=models.PROTECT, null=False, blank=False)
    quantity = models.FloatField(verbose_name=_('Quantity'), null=False, blank=False)
    pallet_configuration = models.ForeignKey(PalletConfiguration, verbose_name='Pallet Configuration', on_delete=models.PROTECT,
                                             related_name="pallet_configuration_supply_expense")

    def __str__(self):
        return f"{self.supply}"

    class Meta:
        verbose_name = _('Supply Expense')
        verbose_name_plural = _('Supply Expenses')
        ordering = ('supply', )
        constraints = [
            models.UniqueConstraint(fields=['supply', 'pallet_configuration'],name='unique_supply_expense_per_pallet_configuration')
        ]

class PalletConfigurationPersonalExpense(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'), null=False, blank=False)
    description = models.CharField(max_length=255, verbose_name=_('Description'), blank=True, null=True)
    cost = models.FloatField(verbose_name=_('Cost'), null=False, blank=False)
    pallet_configuration = models.ForeignKey(PalletConfiguration, verbose_name='Pallet Configuration', on_delete=models.PROTECT,
                                             related_name="pallet_configuration_personal_expense")

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Personal Expense')
        verbose_name_plural = _('Personal Expenses')
        ordering = ('name', )
        constraints = [
            models.UniqueConstraint(fields=['name', 'pallet_configuration'],name='unique_personal_expense_per_pallet_configuration')
        ]


# configuración de productos

class ProductPackaging(CleanNameAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    alias = models.CharField(max_length=20, verbose_name=_('Alias'))

    market = models.ForeignKey(Market, verbose_name=_('Market'), on_delete=models.PROTECT)
    market_class = models.ForeignKey(MarketClass, verbose_name=_('Market class'), on_delete=models.PROTECT)

    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.PROTECT)
    product_variety = models.ForeignKey(ProductVariety, verbose_name=_('Product variety'), on_delete=models.PROTECT)
    product_variety_size = models.ForeignKey(MarketProductSize, verbose_name=_('Product variety size'),
                                             on_delete=models.PROTECT)

    packaging_kind = models.ForeignKey(Packaging, verbose_name=_('Packaging kind'),
                                       on_delete=models.PROTECT)  # TODO: detallar tipos de caja por tipo de producto?
    is_dark = models.BooleanField(default=False, verbose_name=_('Is dark'))
    # TODO: agregar campo para tipo de malla, o no se que va aquí pero falta uno
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Product Packaging')
        verbose_name_plural = _('Product Packaging')
        unique_together = ('name', 'organization')


# Catálogos de exportación
class ExportingCompany(CleanNameAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name / Legal name'))
     ### Localization fields
    country = models.ForeignKey(Country, on_delete=models.PROTECT, verbose_name=_('Country'))
    state = models.ForeignKey(Region, on_delete=models.PROTECT, verbose_name=_('State'))
    city = models.ForeignKey(SubRegion, on_delete=models.PROTECT, verbose_name=_('City'))
    district = models.ForeignKey(City, blank=True, null=True, on_delete=models.PROTECT, verbose_name=_('District'))

    postal_code = models.CharField(max_length=10, verbose_name=_('Postal code'))
    neighborhood = models.CharField(max_length=255, verbose_name=_('Neighborhood'))
    address = models.CharField(max_length=255, verbose_name=_('Address'))
    external_number = models.CharField(max_length=10, verbose_name=_('External number'))
    internal_number = models.CharField(max_length=10, blank=True, null=True, verbose_name=_('Internal number'))

    tax_id = models.CharField(max_length=30, verbose_name=_('Tax ID'))

    contact_name = models.CharField(max_length=255, verbose_name=_('Contact person full name'))
    ### Contact fields
    email = models.EmailField(max_length=255, verbose_name=_('Email'))
    phone_number = models.CharField(max_length=20, verbose_name=_('Phone number'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Exporting Company')
        verbose_name_plural = _('Exporting Companies')
        constraints = [
            models.UniqueConstraint(fields=('name', 'organization',),
                                    name='exporting_company_unique_name_organization'),
        ]

class ExportingCompanyBeneficiary(CleanNameAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    bank = models.ForeignKey(Bank, on_delete=models.PROTECT, verbose_name=_("Bank"))
    bank_account_number = models.CharField(max_length=25, verbose_name=_("Bank account number"))
    interbank_account_number = models.CharField(max_length=20, verbose_name=_('Interbank account number'))
    exporting_company = models.ForeignKey(ExportingCompany, on_delete=models.CASCADE, verbose_name=_("Exporting company"))

    class Meta:
        verbose_name = _("Exporting Company's beneficiary")
        verbose_name_plural = _("Exporting Company's beneficiaries")


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


class HarvestContainer(CleanNameAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    capacity = models.FloatField(verbose_name=_('Capacity'))
    unit_kind = models.CharField(max_length=30, verbose_name=_('Unit kind'), choices=SUPPLY_UNIT_KIND_CHOICES)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name} - {self.capacity} {self.unit_kind}"

    class Meta:
        verbose_name = _('Harvest Container')
        verbose_name_plural = _('Harvest Containers')
        unique_together = ('name', 'organization')
