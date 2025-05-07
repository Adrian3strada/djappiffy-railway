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
from .utils import (vehicle_year_choices, vehicle_validate_year, get_type_choices, get_payment_choices,
                    get_vehicle_category_choices, get_provider_categories_choices)
from django.core.exceptions import ValidationError
from common.base.models import (ProductKind, ProductKindCountryStandardSize, ProductKindCountryStandardPackaging, CapitalFramework,
                                ProductKindCountryStandard, LegalEntityCategory, SupplyKind, PestProductKind, DiseaseProductKind)
from packhouses.packhouse_settings.models import (Bank, VehicleOwnershipKind,
                                                  PaymentKind, VehicleFuelKind, VehicleKind, VehicleBrand,
                                                  AuthorityPackagingKind,
                                                  OrchardCertificationVerifier,
                                                  OrchardCertificationKind)
from .settings import (CLIENT_KIND_CHOICES, ORCHARD_PRODUCT_CLASSIFICATION_CHOICES, PRODUCT_PACKAGING_CATEGORY_CHOICES,
                       PRODUCT_PRICE_MEASURE_UNIT_CATEGORY_CHOICES, PRODUCT_SIZE_CATEGORY_CHOICES)
from common.base.settings import SUPPLY_MEASURE_UNIT_CATEGORY_CHOICES
from common.base.models import FoodSafetyProcedure


# Create your models here.


# Markets

class Market(CleanNameOrAliasAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    alias = models.CharField(max_length=20, verbose_name=_('Alias'))

    
    # Nueva FK obligatoria a Country
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        verbose_name=_('Country'),
        related_name='primary_markets'
    )

    countries = models.ManyToManyField(Country, verbose_name=_('Countries'))

    countries = models.ManyToManyField(
        Country,
        verbose_name=_('Country'),
    )

    is_mixable = models.BooleanField(
        default=True,
        verbose_name=_('Is mixable'),
        help_text=_('Conditional that does not allow mixing fruit with other markets')
    )

    label_language = models.CharField(
        max_length=20,
        verbose_name=_('Label language'),
        choices=settings.LANGUAGES,
        default='es'
    )

    address_label = CKEditor5Field(
        blank=True,
        null=True,
        verbose_name=_('Address of packaging house to show in label'),
        help_text=_('Leave blank to keep the default address defined in the organization')
    )

    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))

    organization = models.ForeignKey(
        Organization,
        verbose_name=_('Organization'),
        on_delete=models.PROTECT
    )

    class Meta:
        verbose_name = _('Market')
        verbose_name_plural = _('Markets')
        ordering = ('organization', 'name')
        constraints = [
            models.UniqueConstraint(fields=['name', 'organization'], name='market_unique_name_organization'),
            models.UniqueConstraint(fields=['alias', 'organization'], name='market_unique_alias_organization')
        ]


# /Markets

# Products

class Product(CleanNameAndOrganizationMixin, models.Model):
    kind = models.ForeignKey(ProductKind, verbose_name=_('Product kind'), on_delete=models.PROTECT)
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    description = models.CharField(blank=True, null=True, max_length=255, verbose_name=_('Description'))
    measure_unit_category = models.CharField(max_length=30, verbose_name=_('Measure unit category'),
                                                   choices=PRODUCT_PRICE_MEASURE_UNIT_CATEGORY_CHOICES)
    markets = models.ManyToManyField(Market, verbose_name=_('Markets'), blank=False)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ('organization', 'kind', 'name')
        constraints = [
            models.UniqueConstraint(fields=['name', 'organization'], name='product_unique_name_organization'),
        ]


class ProductPhenologyKind(CleanNameAndProductMixin, models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.CASCADE)
    sort_order = models.PositiveIntegerField(default=0, verbose_name=_('Sort order'))

    class Meta:
        verbose_name = _('Product phenology kind')
        verbose_name_plural = _('Product phenology kinds')
        ordering = ('product', 'sort_order',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'product'], name='productphenologykind_unique_name_product'),
        ]


class ProductMarketMeasureUnitManagementCost(models.Model):
    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.CASCADE)
    market = models.ForeignKey(Market, verbose_name=_('Market'), on_delete=models.PROTECT)
    measure_unit_management_cost = models.CharField(max_length=100, verbose_name=_('Measure unit management cost'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))

    def __str__(self):
        return f"{self.product.name} ({self.market.name} ): {self.measure_unit_management_cost}"

    class Meta:
        verbose_name = _('Product market measure unit management cost')
        verbose_name_plural = _('Product market measure unit management costs')
        ordering = ('market', 'product', 'measure_unit_management_cost')
        constraints = [
            models.UniqueConstraint(fields=['product', 'market'],
                                    name='productmarketmeasureunitmanagementcost_product_market'),
        ]


class ProductMarketClass(models.Model):
    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.CASCADE)
    market = models.ForeignKey(Market, verbose_name=_('Market'), on_delete=models.PROTECT)
    name = models.CharField(max_length=100, verbose_name=_('Class name'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))

    def __str__(self):
        return f"{self.product.name} ({self.market.name} ): {self.name}"

    class Meta:
        verbose_name = _('Product market class')
        verbose_name_plural = _('Product market class')
        ordering = ('market', 'product', 'name')
        constraints = [
            models.UniqueConstraint(fields=['product', 'market', 'name'],
                                    name='productmarketclass_product_market_name'),
        ]


class ProductVariety(CleanNameAndAliasProductMixin, models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Variety name'))
    alias = models.CharField(max_length=20, verbose_name=_('Alias'))
    description = models.CharField(blank=True, null=True, max_length=255, verbose_name=_('Description'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Product variety')
        verbose_name_plural = _('Product varieties')
        ordering = ('product', 'name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'product'], name='product_unique_name_product'),
            models.UniqueConstraint(fields=['alias', 'product'], name='product_unique_alias_product'),
        ]


class ProductHarvestSizeKind(CleanProductMixin, models.Model):
    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.CASCADE)
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


class ProductRipeness(CleanProductMixin, models.Model):
    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))

    class Meta:
        verbose_name = _('Product ripeness')
        verbose_name_plural = _('Product Ripeness')
        ordering = ('product', 'name')
        constraints = [
            models.UniqueConstraint(fields=['name', 'product'],
                                    name='productripeness_unique_name_product'),
        ]


class ProductSize(CleanNameAndAliasProductMixin, models.Model):
    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.PROTECT)
    varieties = models.ManyToManyField(ProductVariety, verbose_name=_('Varieties'), blank=False)
    market = models.ForeignKey(Market, verbose_name=_('Market'), on_delete=models.PROTECT)
    category = models.CharField(max_length=30, verbose_name=_('Category'), choices=PRODUCT_SIZE_CATEGORY_CHOICES)
    standard_size = models.ForeignKey(
    ProductKindCountryStandardSize,
    verbose_name=_('Standard size'),
    on_delete=models.PROTECT,
    null=True,
    blank=True,
)

    name = models.CharField(max_length=160, verbose_name=_('Name'))
    alias = models.CharField(max_length=20, verbose_name=_('Alias'))
    description = models.CharField(max_length=255, verbose_name=_('Description'), blank=True, null=True)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    sort_order = models.PositiveIntegerField(default=0, verbose_name=_('Sort order'))

    class Meta:
        verbose_name = _('product size')
        verbose_name_plural = _('product sizes')
        ordering = ['sort_order']
        constraints = [
            models.UniqueConstraint(fields=['name', 'product', 'market'],
                                    name='productsize_unique_name_product_market'),
            models.UniqueConstraint(fields=['alias', 'product', 'market'],
                                    name='productsize_unique_alias_product_market'),
        ]


class ProductPest(models.Model):
    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.CASCADE)
    pest = models.ForeignKey(PestProductKind, verbose_name=_('Pest'), on_delete=models.CASCADE)
    name = models.CharField(max_length=255, unique=False)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['product', 'pest', 'name'],
                                    name='unique_product_pest_name')
        ]

class ProductDisease(models.Model):
    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.CASCADE)
    disease = models.ForeignKey(DiseaseProductKind, verbose_name=_('Disease'), on_delete=models.CASCADE)
    name = models.CharField(max_length=255, unique=False)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['product', 'disease', 'name'],
                                    name='unique_product_disease_name')
        ]

class ProductPhysicalDamage(models.Model):
    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.CASCADE)
    name = models.CharField(max_length=255, unique=False)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ['name']
        verbose_name = _('Product physical damage')
        verbose_name_plural = _('Product physical damages')
        ordering = ('name', 'product')
        constraints = [
            models.UniqueConstraint(fields=['name', 'product'],
                                    name='productphysicaldamage_unique_name_product'),
        ]

class ProductResidue(models.Model):
    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.CASCADE)
    name = models.CharField(max_length=255, unique=False)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ['name']
        verbose_name = _('Product residue')
        verbose_name_plural = _('Product Residues')
        ordering = ('name', 'product')
        constraints = [
            models.UniqueConstraint(fields=['name', 'product'],
                                    name='productresidue_unique_name_product'),
        ]

class ProductFoodSafetyProcess(models.Model):
    procedure = models.ForeignKey(FoodSafetyProcedure, verbose_name=_('Food Safety Procedure'), on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.CASCADE)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))

    def __str__(self):
        return f"{self.procedure}"

    class Meta:
        verbose_name = _('Product Food Safety Process')
        verbose_name_plural = _('Product Food Safety Process')
        constraints = [
            models.UniqueConstraint(fields=['procedure', 'product'],
                                    name='productfoodsafetyprocess_unique_procedure_product'),
        ]

class ProductDryMatterAcceptanceReport(models.Model):
    acceptance_report = models.IntegerField(verbose_name=_('Dry Matter Acceptance Report'), null=True, blank=True)
    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))

    def __str__(self):
        return f"{self.acceptance_report}"

    class Meta:
        ordering = ('-created_at',)
        verbose_name = _('Product Additional Value')
        verbose_name_plural = _('Product Additional Values')

    def save_model(self, request, obj, form, change):
        latest = ProductDryMatterAcceptanceReport.objects.order_by('-created_at').first()
        if obj.pk != latest.pk:
            return  # No guardar si no es el último
        super().save_model(request, obj, form, change)

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
            models.UniqueConstraint(fields=['serial_number', 'organization'],
                                    name='vehicle_unique_serial_number_organization'),
        ]


# /Vehicles


# Providers

class Provider(CleanNameAndCategoryAndOrganizationMixin, models.Model):
    ### Identification fields
    name = models.CharField(max_length=255, verbose_name=_('Full name'))

    ### Provider Category
    category = models.CharField(max_length=255, choices=get_provider_categories_choices(), verbose_name=_('Category'))

    ### Reference to implied Provider (for producers)
    provider_provider = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                          verbose_name=_('Provider'))

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
            models.UniqueConstraint(fields=['name', 'category', 'organization'],
                                    name='provider_unique_name_organization'),
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
        return f"{self.pk}: {self.provider.name}"

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
    shipping_address = models.OneToOneField('catalogs.ClientShippingAddress',
                                            verbose_name=_('Shipping address'),
                                            help_text=_(
                                                'Shipping address of the client, leave it blank if you want to use the client address for shipping, or select one if you want to use a different one.'),
                                            on_delete=models.PROTECT, null=True, blank=True,
                                            related_name='shipping_address_clients')
    capital_framework = models.ForeignKey(CapitalFramework, verbose_name=_('Capital framework'),
                                          null=True, blank=True,
                                          on_delete=models.PROTECT, help_text=_(
            'Legal category of the client, must have a country selected to show that country legal categories.'))
    tax_id = models.CharField(max_length=30, verbose_name=_('Client tax ID'))
    payment_kind = models.ForeignKey(PaymentKind, verbose_name=_('Payment kind'), on_delete=models.PROTECT)
    max_money_credit_limit = models.FloatField(default=0, verbose_name=_('Max money credit limit'))
    max_days_credit_limit = models.FloatField(default=0, verbose_name=_('Max days credit limit'))
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
            models.UniqueConstraint(fields=('name', 'category', 'organization',),
                                    name='client_unique_name_category_organization'),
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
            models.UniqueConstraint(fields=('address_name', 'client',),
                                    name='clientshippingaddress_unique_address_name_client'),
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
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT,
                                help_text=_("Only shows the vehicles that belongs to 'packhouse' category"))
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
    clients = models.ManyToManyField(Client, verbose_name=_('Clients'), blank=False,
                                     help_text=_(
                                         'Clients associated with this maquiladora, it must be created before at Catalogs:Clients section.'))

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
    category = models.CharField(max_length=100, verbose_name=_('Product category'),
                                choices=ORCHARD_PRODUCT_CLASSIFICATION_CHOICES)
    product = models.ManyToManyField(Product, verbose_name=_('Product'), blank=True, )
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
        return f"{self.orchard.name}: {self.certification_kind.name}"

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
                                     help_text=_("From how many KG will the full truck payment be considered?"),
                                     validators=[MinValueValidator(0.01)])

    pay_per_box_complete = models.FloatField(verbose_name=_('Pay per box (full truck)'),
                                             help_text=_("Payment per box in case of full truck"),
                                             validators=[MinValueValidator(0.01)])
    pay_per_kg_complete = models.FloatField(verbose_name=_('Pay per kg (full truck)'),
                                            help_text=_("Payment per kg in case of full truck"),
                                            validators=[MinValueValidator(0.01)])
    pay_per_day_complete = models.FloatField(verbose_name=_('Pay per day (full truck)'),
                                             help_text=_("Payment per day in case of full truck"),
                                             validators=[MinValueValidator(0.01)])

    pay_per_box_incomplete = models.FloatField(verbose_name=_('Pay per box (incomplete truck)'),
                                               help_text=_("Payment per box in case of incomplete truck"),
                                               validators=[MinValueValidator(0.01)])
    pay_per_kg_incomplete = models.FloatField(verbose_name=_('Pay per kg (incomplete truck)'),
                                              help_text=_("Payment per kg in case of incomplete truck"),
                                              validators=[MinValueValidator(0.01)])
    pay_per_day_incomplete = models.FloatField(verbose_name=_('Pay per day (incomplete truck)'),
                                               help_text=_("Payment per day in case of incomplete truck"),
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


# Insumos


class Supply(CleanNameAndOrganizationMixin, models.Model):
    kind = models.ForeignKey(SupplyKind, verbose_name=_('Kind'), on_delete=models.PROTECT)
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    capacity = models.FloatField(verbose_name=_('Capacity'), validators=[MinValueValidator(0.01)],
                                 null=True, blank=True,
                                 help_text=_('Capacity of the supply, based in the usage unit'))

    minimum_stock_quantity = models.PositiveIntegerField(verbose_name=_('Minimum stock quantity'))
    maximum_stock_quantity = models.PositiveIntegerField(verbose_name=_('Maximum stock quantity'))
    usage_discount_quantity = models.FloatField(verbose_name=_('Usage discount quantity'),
                                                          validators=[MinValueValidator(0.01)],
                                                          help_text=_(
                                                              'Amount of units to discount when a supply is consumed, based in the usage unit of the supply kind'))
    kg_tare = models.FloatField(default=0, verbose_name=_("Kg tare"), null=True, blank=True, )
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        if self.kind.category == 'packaging_presentation':
            capacity = int(self.capacity) if self.capacity % 1 == 0 else self.capacity
            unit = _(
                'piece') if self.kind.capacity_unit_category == 'pieces' and capacity == 1 else self.kind.capacity_unit_category
            return f"{self.kind.name}: {self.name} ({capacity} {unit})"
        return f"{self.kind.name}: {self.name}"

    def clean(self):
        value = self.capacity
        if self.kind.category in ['packaging_containment', 'packaging_presentation',
                                  'packaging_storage', 'packhouse_cleaning', 'packhouse_fuel', 'harvest_container']:
            min_value = 1 if self.kind.capacity_unit_category in ['pieces'] else 0.01
            validation_error = _('Capacity must be at least 1 for this kind.') if self.kind.capacity_unit_category in [
                'pieces'] else _('Capacity must be at least 0.01 for this kind.')
            if value and value < min_value:
                raise ValidationError(
                    validation_error,
                    params={'capacity': value},
                )

        elif self.kind.category in ['packaging_separator']:
            if value and value < 0:
                raise ValidationError(
                    _('Capacity can be at minimum 0 for this kind.'),
                    params={'capacity': value},
                )
        else:
            if value is not None:
                raise ValidationError(
                    _('Capacity cannot has value for this kind category.'),
                    params={'capacity': value},
                )

        return super().clean()

    class Meta:
        verbose_name = _('Supply')
        verbose_name_plural = _('Supplies')
        ordering = ('organization', 'kind', 'name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'organization'], name='supply_unique_name_organization'),
        ]


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


# Pallets


class Pallet(models.Model):
    market = models.ForeignKey(Market, verbose_name=_('Market'), on_delete=models.PROTECT)
    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.PROTECT)
    supply = models.ForeignKey(Supply, verbose_name=_('Supply'), on_delete=models.PROTECT,
                               limit_choices_to={'kind__category': 'packaging_pallet'})
    name = models.CharField(max_length=255, verbose_name=_('Name'), null=False, blank=False)
    alias = models.CharField(max_length=20, verbose_name=_('Alias'), null=False, blank=False)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Pallet')
        verbose_name_plural = _('Pallets')
        ordering = ('name', 'market', 'product', 'supply', 'organization')
        constraints = [
            models.UniqueConstraint(fields=['market', 'product', 'supply', 'organization'],
                                    name='pallet_configuration_unique_market_product_supply_organization'),
            models.UniqueConstraint(fields=['name', 'organization'],
                                    name='pallet_configuration_unique_name_organization'),
            models.UniqueConstraint(fields=['alias', 'organization'],
                                    name='pallet_configuration_unique_alias_organization')
        ]


class PalletComplementarySupply(models.Model):
    pallet = models.ForeignKey(Pallet, verbose_name='Pallet Configuration', on_delete=models.CASCADE)
    kind = models.ForeignKey(SupplyKind, verbose_name=_('Kind'), on_delete=models.PROTECT,
                             limit_choices_to={'category': 'packaging_pallet_complement'})
    supply = models.ForeignKey(Supply, verbose_name=_('Supply'), on_delete=models.PROTECT,
                               limit_choices_to={'kind__category': 'packaging_pallet_complement'})
    quantity = models.IntegerField(verbose_name=_('Quantity'), validators=[MinValueValidator(1)])

    def __str__(self):
        return f"{self.supply}"

    class Meta:
        verbose_name = _('Pallet Complementary supply')
        verbose_name_plural = _('Pallet Complementary supplies')
        ordering = ('supply', 'kind', 'pallet')
        constraints = [
            models.UniqueConstraint(fields=['kind', 'supply', 'pallet'],
                                    name='productpackagingpalletcomplementarysupply_unique_kind_supply_pallet')
        ]


# Tipos de empaques


class ProductPresentation(CleanNameAndOrganizationMixin, models.Model):
    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.PROTECT)
    markets = models.ManyToManyField(Market, verbose_name=_('Markets'))
    presentation_supply_kind = models.ForeignKey(SupplyKind, verbose_name=_('Presentation supply kind'),
                                                 limit_choices_to={'category': 'packaging_presentation'},
                                                 on_delete=models.PROTECT)
    presentation_supply = models.ForeignKey(Supply, verbose_name=_('Presentation supply'),
                                            limit_choices_to={'kind__category': 'packaging_presentation'},
                                            on_delete=models.PROTECT)
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Product presentation')
        verbose_name_plural = _('Product presentations')
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(fields=('product', 'name', 'organization'),
                                    name='productpresentation_unique_product_name_organization'),
        ]


class ProductPresentationComplementarySupply(models.Model):
    product_presentation = models.ForeignKey(ProductPresentation, on_delete=models.CASCADE)
    kind = models.ForeignKey(SupplyKind, verbose_name=_('Kind'),
                             limit_choices_to={'category': 'packaging_presentation_complement'},
                             on_delete=models.PROTECT)
    supply = models.ForeignKey(Supply, verbose_name=_('Supply'), on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Product presentation complementary supply')
        verbose_name_plural = _('Product presentation complementary supplies')
        ordering = ('kind', 'supply')
        constraints = [
            models.UniqueConstraint(fields=('product_presentation', 'kind', 'supply'),
                                    name='productpresentationcomplementarysupply_unique_productpresentation_kind_supply'),
        ]


class Packaging(models.Model):
    market = models.ForeignKey(Market, verbose_name=_('Market'), on_delete=models.PROTECT)
    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.PROTECT)
    packaging_supply_kind = models.ForeignKey(SupplyKind, verbose_name=_('Packaging supply kind'),
                                              on_delete=models.PROTECT)
    country_standard_packaging = models.ForeignKey(ProductKindCountryStandardPackaging,
                                                   verbose_name=_('Country standard packaging'),
                                                   null=True, blank=True, on_delete=models.PROTECT)
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    packaging_supply = models.ForeignKey(Supply, verbose_name=_('Packaging supply'), on_delete=models.PROTECT)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    clients = models.ManyToManyField('Client', verbose_name=_('Clients'), blank=True)
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('packaging')
        verbose_name_plural = _('packaging')
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(fields=('market', 'product', 'name', 'organization'),
                                    name='packaging_unique_market_product_name_organization'),
        ]


class PackagingComplementarySupply(models.Model):
    packaging = models.ForeignKey(Packaging, on_delete=models.CASCADE)
    kind = models.ForeignKey(SupplyKind, verbose_name=_('Kind'), on_delete=models.PROTECT)
    supply = models.ForeignKey(Supply, verbose_name=_('Supply'), on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(verbose_name=_('Quantity'), validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = _('Product packaging complementary supply')
        verbose_name_plural = _('Product packaging complementary supplies')
        ordering = ('kind', 'supply')
        constraints = [
            models.UniqueConstraint(fields=('packaging', 'kind', 'supply'),
                                    name='productpackagingcomplementarysupply_unique_packaging_kind_supply'),
        ]


class ProductPackaging(CleanNameAndOrganizationMixin, models.Model):
    category = models.CharField(max_length=20, choices=PRODUCT_PACKAGING_CATEGORY_CHOICES, verbose_name=_('Category'))
    market = models.ForeignKey(Market, verbose_name=_('Market'), on_delete=models.PROTECT, limit_choices_to={'is_enabled': True})
    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.PROTECT)
    product_size = models.ForeignKey(ProductSize, verbose_name=_('Product size'), on_delete=models.PROTECT)
    packaging = models.ForeignKey(Packaging, verbose_name=_('Packaging'), on_delete=models.CASCADE)
    product_weight_per_packaging = models.FloatField(verbose_name=_('Product weight per packaging'),
                                                     validators=[MinValueValidator(0.01)])
    product_presentation = models.ForeignKey(ProductPresentation, verbose_name=_('Product presentation'),
                                             null=True, blank=True, on_delete=models.CASCADE)
    product_presentations_per_packaging = models.PositiveIntegerField(
        verbose_name=_('Product presentations per packaging'),
        null=True, blank=True, validators=[MinValueValidator(1)])
    product_pieces_per_presentation = models.PositiveIntegerField(verbose_name=_('Product pieces per presentation'),
                                                                  null=True, blank=True, validators=[MinValueValidator(1)])
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    alias = models.CharField(max_length=30, verbose_name=_('Alias'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Product packaging')
        verbose_name_plural = _('Product packaging')
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=('market', 'product', 'product_size', 'packaging', 'product_presentation', 'organization'),
                name='productpackaging_unique_market_product_productsize_packaging_productpresentation_organization'),
            models.UniqueConstraint(fields=('name', 'organization'), name='productpackaging_unique_name_organization'),
            models.UniqueConstraint(fields=('alias', 'organization'),
                                    name='productpackaging_unique_alias_organization'),
        ]


class ProductPackagingPresentation(models.Model):
    product_packaging = models.ForeignKey(ProductPackaging, on_delete=models.CASCADE)
    product_presentation = models.ForeignKey(ProductPresentation, verbose_name=_('presentation'),
                                             on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name=_('Quantity'),
                                           help_text=_('Amount of product presentations for this product packaging'),
                                           validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = _('Product packaging presentation')
        verbose_name_plural = _('Product packaging presentations')
        ordering = ('product_packaging', 'product_presentation')
        constraints = [
            models.UniqueConstraint(fields=('product_packaging', 'product_presentation'),
                                    name='productpackagingpresentation_unique_productpackaging_presentation'),
        ]


class ProductPackagingPallet(models.Model):
    product_packaging = models.ForeignKey(ProductPackaging, on_delete=models.CASCADE)
    pallet = models.ForeignKey(Pallet, on_delete=models.CASCADE)
    product_packaging_quantity = models.PositiveIntegerField(verbose_name=_('Product packaging quantity'),
                                                             help_text=_(
                                                             'Amount of product packaging units for this pallet.'),
                                                             validators=[MinValueValidator(1)])
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))

    def __str__(self):
        return f"{self.product_packaging} - {self.pallet} ({self.product_packaging_quantity})"

    class Meta:
        verbose_name = _('Product packaging pallet')
        verbose_name_plural = _('Product packaging pallets')
        ordering = ('product_packaging', 'pallet')
        constraints = [
            models.UniqueConstraint(fields=('product_packaging', 'pallet', 'product_packaging_quantity'),
                                    name='productpackagingpallet_unique_productpackaging_pallet_product_packaging_quantity'),
        ]


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


# configuración de productos


# Catálogos de exportación
class ExportingCompany(CleanNameAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name / Legal name'))
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
    exporting_company = models.ForeignKey(ExportingCompany, on_delete=models.CASCADE,
                                          verbose_name=_("Exporting company"))

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
