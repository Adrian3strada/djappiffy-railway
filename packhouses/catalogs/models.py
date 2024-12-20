from django.db import models
from common.mixins import (CleanKindAndOrganizationMixin, CleanNameAndOrganizationMixin,
                           CleanNameOrAliasAndOrganizationMixin, CleanNameAndMarketMixin, CleanNameAndProductMixin,
                           CleanNameAndProductProviderMixin, CleanNameAndProductProducerMixin,
                           CleanNameAndVarietyAndMarketAndVolumeKindMixin, CleanNameAndMaquiladoraMixin)
from organizations.models import Organization
from cities_light.models import City, Country, Region
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django_ckeditor_5.fields import CKEditor5Field
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from common.billing.models import TaxRegime, LegalEntityCategory
from .utils import vehicle_year_choices, vehicle_validate_year
from django.core.exceptions import ValidationError
from common.base.models import ProductKind
from packhouses.packhouse_settings.models import (ProductSizeKind, MassVolumeKind, Bank, VehicleOwnershipKind,
                                                  PaymentKind, VehicleFuelKind, VehicleKind, VehicleBrand,
                                                  OrchardProductClassificationKind, OrchardCertificationVerifier,
                                                  OrchardCertificationKind)


# Create your models here.


class Market(CleanNameOrAliasAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    alias = models.CharField(max_length=20, verbose_name=_('Alias'))
    # country = models.ForeignKey(Country, verbose_name=_('Country'), default=158, on_delete=models.PROTECT, related_name='markets_country')
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
                errors['name'] = _('Name must be unique, it already exists.')

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('Market standard product size')
        verbose_name_plural = _('Market standard product sizes')
        ordering = ('market', 'order',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'market'], name='marketstandardproductsize_unique_name_market'),
        ]


class Product(CleanKindAndOrganizationMixin, models.Model):
    kind = models.ForeignKey(ProductKind, verbose_name=_('Product kind'), on_delete=models.PROTECT)
    description = models.CharField(blank=True, null=True, max_length=255, verbose_name=_('Description'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ('organization', 'kind')
        constraints = [
            models.UniqueConstraint(fields=['kind', 'organization'], name='product_unique_kind_organization'),
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


class ProductHarvestKind(CleanNameAndProductMixin, models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.PROTECT)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    order = models.IntegerField(default=0, verbose_name=_('Order'))

    class Meta:
        verbose_name = _('Product harvest Kind')
        verbose_name_plural = _('Product harvest kinds')
        ordering = ('product', 'order',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'product'], name='productharvestkind_unique_name_product'),
        ]


class ProductVarietySize(CleanNameAndVarietyAndMarketAndVolumeKindMixin, models.Model):
    variety = models.ForeignKey(ProductVariety, verbose_name=_('Variety'), on_delete=models.PROTECT)
    market = models.ForeignKey(Market, verbose_name=_('Market'), on_delete=models.PROTECT)
    market_standard_size = models.ForeignKey(MarketStandardProductSize,
                                             verbose_name=_('Market standard product size'),
                                             help_text=_(
                                                 'Choose a Standard Product Size per Market (optional), it will put its name in the size name field.'),
                                             on_delete=models.PROTECT, null=True, blank=True)
    name = models.CharField(max_length=160, verbose_name=_('Size name'))
    alias = models.CharField(max_length=20, verbose_name=_('Alias'))
    description = models.CharField(blank=True, null=True, max_length=255, verbose_name=_('Description'))
    size_kind = models.ForeignKey(ProductSizeKind, verbose_name=_('Size kind'),
                                  on_delete=models.PROTECT)  # Normal, roña, etc
    harvest_kind = models.ForeignKey(ProductHarvestKind, verbose_name=_('Harvest kind'),
                                     on_delete=models.PROTECT)  # Tipos de corte
    volume_kind = models.ForeignKey(MassVolumeKind, verbose_name=_('Volume kind'), on_delete=models.PROTECT,
                                    help_text=_('To separate sizes by product kind in the mass volume report'))
    requires_corner_protector = models.BooleanField(default=False, verbose_name=_('Requires corner protector'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    order = models.PositiveIntegerField(default=0,
                                        verbose_name=_('Order'))  # TODO: implementar ordenamiento con drag and drop

    @property
    def product_name(self):
        return self.variety.product.name if self.variety and self.variety.product else None

    def __str__(self):
        return f"{self.variety.product.name}: {self.variety.name} ({self.name})"

    class Meta:
        verbose_name = _('Product variety size')
        verbose_name_plural = _('Product variety sizes')
        ordering = ['variety', 'order']
        constraints = [
            models.UniqueConstraint(fields=['name', 'variety', 'market', 'volume_kind'],
                                    name='productvarietysize_unique_name_variety_market_volumekind'),
        ]


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
    district = models.CharField(max_length=255, verbose_name=_('District'))
    neighborhood = models.CharField(max_length=255, verbose_name=_('Neighborhood'))
    postal_code = models.CharField(max_length=10, verbose_name=_('Postal code'))
    address = models.CharField(max_length=255, verbose_name=_('Address'))
    external_number = models.CharField(max_length=20, verbose_name=_('External number'))
    internal_number = models.CharField(max_length=20, verbose_name=_('Internal number'))
    tax_id = models.CharField(max_length=100, verbose_name=_('Tax ID'))
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, verbose_name=_('Phone number'))
    product_provider = models.ForeignKey(ProductProvider, on_delete=models.PROTECT, verbose_name=_('Product provider'))
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
    country = models.ForeignKey(Country, verbose_name=_('Country'), on_delete=models.PROTECT)  # TODO: verificar si se necesita país, pues ya el mercado tiene país
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
    fuel = models.ForeignKey(VehicleFuelKind, verbose_name=_('Fuel kind'), on_delete=models.PROTECT)
    comments = models.CharField(max_length=250, verbose_name=_('Comments'), blank=True, null=True)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Vehicle')
        verbose_name_plural = _('Vehicles')
        ordering = ('organization', 'name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'organization'], name='vehicle_unique_name_organization'),
            models.UniqueConstraint(fields=['license_plate', 'organization'], name='vehicle_unique_licenseplate_organization'),
            models.UniqueConstraint(fields=['serial_number', 'organization'], name='vehicle_unique_serialnumber_organization')
        ]


# Acopiadores


class Gatherer(CleanNameAndOrganizationMixin, models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Full name'))
    zone = models.CharField(max_length=200, verbose_name=_('Zone'))
    tax_registry_code = models.CharField(max_length=20, verbose_name=_('Tax registry code'))
    population_registry_code = models.CharField(max_length=20, verbose_name=_('Population registry code'), null=True, blank=True)
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
    population_registry_code = models.CharField(max_length=20, verbose_name=_('Population registry code'), null=True, blank=True)
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
                                       on_delete = models.PROTECT, help_text = _('Legal category of the client, must have a country selected to show that country legal categories.'))
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
    safety_authority_registration_date = models.DateField(verbose_name=_('Registration date'))
    state = models.ForeignKey(Region, verbose_name=_('State'), on_delete=models.PROTECT)
    city = models.ForeignKey(City, verbose_name=_('City'), on_delete=models.PROTECT)
    district = models.CharField(max_length=255, verbose_name=_('District'), null=True, blank=True)
    ha = models.FloatField(verbose_name=_('Hectares'))
    product_classification_kind = models.ForeignKey(OrchardProductClassificationKind, verbose_name=_('Product Classification'),
                                                    on_delete=models.PROTECT)
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



class OrchardCertification(models.Model):
    certification_kind = models.ForeignKey(OrchardCertificationKind, verbose_name=_('Orchard certification kind'),
                                           on_delete=models.PROTECT)
    certification_number = models.CharField(max_length=100, verbose_name=_('Certification number'))
    expiration_date = models.DateField(verbose_name=_('Expiration date'))
    verifier = models.ForeignKey(OrchardCertificationVerifier, verbose_name=_('Orchard certification verifier'),
                                 on_delete=models.PROTECT)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    orchard = models.ForeignKey(Orchard, verbose_name=_('Orchard'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.orchard.name} : {self.certification_kind.name}"

    class Meta:
        verbose_name = _('Orchard certification')
        verbose_name_plural = _('Orchard certifications')
        unique_together = ('orchard', 'certification_kind')
        ordering = ('orchard', 'certification_kind')


# Cuadrillas de cosecha

class HarvestCrew(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))

    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Harvest crew')
        verbose_name_plural = _('Harvest crews')
        unique_together = ('name', 'organization')
        ordering = ('name',)


#  Proveedores de insumos


class SupplyUnitKind(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Supply unit kind')
        verbose_name_plural = _('Supply unit kinds')
        unique_together = ('name', 'organization')
        ordering = ('name',)


class SupplyKind(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Supply kind')
        verbose_name_plural = _('Supply kinds')
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
        verbose_name = _('Supply kind relation')
        verbose_name_plural = _('Supply kind relations')


class Supply(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    unit_cost = models.FloatField(verbose_name=_('Unit cost'))
    unit_price = models.FloatField(verbose_name=_('Unit price'))
    unit_quantity = models.PositiveIntegerField(verbose_name=_('Unit quantity'))
    unit_kind = models.ForeignKey(SupplyUnitKind, verbose_name=_('Unit kind'), on_delete=models.PROTECT)
    minimum_stock_quantity = models.PositiveIntegerField(verbose_name=_('Minimum stock quantity'))
    maximum_stock_quantity = models.PositiveIntegerField(verbose_name=_('Maximum stock quantity'))
    kind = models.ForeignKey(SupplyKind, verbose_name=_('Kind'), on_delete=models.PROTECT)
    is_tray = models.BooleanField(default=False, verbose_name=_('Is tray'))
    related_supply = models.ForeignKey('self', verbose_name=_('Related supply'), null=True, blank=True,
                                       on_delete=models.SET_NULL, related_name='related_supplies')
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Supply')
        verbose_name_plural = _('Supplies')
        unique_together = ('name', 'organization')
        ordering = ('name',)


class Supplier(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    tax_id = models.CharField(max_length=100, verbose_name=_('Tax ID'))
    state = models.ForeignKey(Region, verbose_name=_('State'), on_delete=models.PROTECT)
    city = models.ForeignKey(City, verbose_name=_('City'), on_delete=models.PROTECT)
    district = models.CharField(max_length=255, verbose_name=_('District'), null=True, blank=True)
    neighborhood = models.CharField(max_length=255, verbose_name=_('Neighborhood'), null=True, blank=True)
    postal_code = models.CharField(max_length=10, verbose_name=_('Postal code'))
    address = models.CharField(max_length=255, verbose_name=_('Address'))
    external_number = models.CharField(max_length=20, verbose_name=_('External number'))
    internal_number = models.CharField(max_length=20, verbose_name=_('Internal number'))
    payment_kind = models.ForeignKey(PaymentKind, verbose_name=_('Payment kind'), on_delete=models.PROTECT)
    credit_days = models.PositiveIntegerField(verbose_name=_('Credit days'))
    balance = models.FloatField(verbose_name=_('Balance'))
    supplies = models.ManyToManyField(Supply, verbose_name=_('Supplies'))
    comments = models.CharField(max_length=250, verbose_name=_('Comments'), blank=True, null=True)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Supplier')
        verbose_name_plural = _('Suppliers')
        unique_together = ('name', 'organization')


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
