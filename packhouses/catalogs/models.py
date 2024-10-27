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
    alias = models.CharField(max_length=20, verbose_name=_('Alias'))
    country = models.ForeignKey(Country, verbose_name=_('Country'), default=158, on_delete=models.PROTECT)
    management_cost_per_kg = models.FloatField(verbose_name=_('Management cost per Kg'), validators=[MinValueValidator(0.01)], help_text=_('Cost generated per Kg for product management and packaging'))
    is_foreign = models.BooleanField(default=False, verbose_name=_('Is foreign'), help_text=_('Conditional for performance reporting to separate foreign and domestic markets; separation in the report of volume by mass and customer addresses'))
    is_mixable = models.BooleanField(default=False, verbose_name=_('Is mixable'), help_text=_('Conditional that does not allow mixing fruit with other markets'))
    label_language = models.CharField(max_length=20, verbose_name=_('Label language'), choices=settings.LANGUAGES, default='es')
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
        verbose_name = _('Cost per Kg on Market')
        verbose_name_plural = _('Costs per Kg on Market')
        unique_together = ('name', 'market')
        ordering = ('name',)


class MarketClass(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    market = models.ForeignKey(Market, verbose_name=_('Market'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Market class')
        verbose_name_plural = _('Market classes')
        unique_together = ('name', 'market')
        ordering = ('name',)


class ProductQualityKind(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Description'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Product quality kind')
        verbose_name_plural = _('Product quality kinds')
        unique_together = ('name', 'organization')
        ordering = ('name',)


class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Description'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        unique_together = ('name', 'organization')


class ProductVariety(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Description'))
    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.product.name} : {self.name}"

    class Meta:
        verbose_name = _('Product variety')
        verbose_name_plural = _('Product varieties')
        unique_together = ('name', 'product')
        ordering = ('name',)


class ProductVarietyHarvestKind(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Description'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Product variety harvest Kind')
        verbose_name_plural = _('Product variety harvest kinds')
        unique_together = ('name', 'organization')
        ordering = ('name',)


class ProductVarietySizeKind(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Description'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Product variety size kind')
        verbose_name_plural = _('Product variety size kinds')
        unique_together = ('name', 'organization')
        ordering = ('name',)


class ProductVarietySize(models.Model):
    variety = models.ForeignKey(ProductVariety, verbose_name=_('Variety'), on_delete=models.PROTECT)
    market = models.ForeignKey(Market, verbose_name=_('Market'), on_delete=models.PROTECT)
    quality_kind = models.ForeignKey(ProductQualityKind, verbose_name=_('Quality kind'), on_delete=models.PROTECT)
    name = models.CharField(max_length=160, verbose_name=_('Size name'))
    alias = models.CharField(max_length=20, verbose_name=_('Alias'))
    # apeam... TODO: generalizar esto para que no sea solo apeam
    harvest_kind = models.ForeignKey(ProductVarietyHarvestKind, verbose_name=_('Harvest kind'), on_delete=models.PROTECT)
    description = models.CharField(max_length=255, verbose_name=_('Description'))
    size_kind = models.ForeignKey(ProductVarietySizeKind, verbose_name=_('Size kind'), on_delete=models.PROTECT, help_text=_('To separate sizes by kind in the mass volume report'))
    requires_corner_protector = models.BooleanField(default=False, verbose_name=_('Requires corner protector'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Order'))  # TODO: implementar ordenamiento con drag and drop

    def __str__(self):
        return f"{self.variety.product.name} : {self.variety.name} : {self.name}"

    class Meta:
        verbose_name = _('Product variety size')
        verbose_name_plural = _('Product variety sizes')
        unique_together = ('name', 'market', 'variety')
        ordering = ['order']


# Proveedores de fruta:

class Bank(models.Model):
    name = models.CharField(max_length=120, verbose_name=_('Name'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Bank')
        verbose_name_plural = _('Banks')
        unique_together = ('name', 'organization')
        ordering = ('name',)


class ProductProvider(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Full name'))
    alias = models.CharField(max_length=20, verbose_name=_('Alias'))
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


class ProductProviderBenefactor(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Full name'))
    bank_account_number = models.CharField(max_length=20, verbose_name=_('Bank account number'))
    bank = models.ForeignKey(Bank, on_delete=models.PROTECT, verbose_name=_('Bank'))
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
    name = models.CharField(max_length=255, verbose_name=_('Full name'))
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
    product_provider = models.ForeignKey(ProductProvider, on_delete=models.PROTECT, verbose_name=_('Product provider'))
    bank_account_number = models.CharField(max_length=20, verbose_name=_('Bank account number'))
    bank = models.ForeignKey(Bank, on_delete=models.PROTECT, verbose_name=_('Bank'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Product producer')
        verbose_name_plural = _('Product producers')
        unique_together = ('name', 'organization')
        ordering = ('name',)


class ProductProducerBenefactor(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    bank_account_number = models.CharField(max_length=20, verbose_name=_('Bank account number'))
    bank = models.ForeignKey(Bank, on_delete=models.PROTECT, verbose_name=_('Bank'))
    product_producer = models.ForeignKey(ProductProducer, on_delete=models.CASCADE, verbose_name=_('Product producer'))

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Product producer benefactor')
        verbose_name_plural = _('Product producer benefactors')
        unique_together = ('name', 'product_producer')
        ordering = ('name',)


class PaymentKind(models.Model):
    name = models.CharField(max_length=120, verbose_name=_('Name'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Payment kind')
        verbose_name_plural = _('Payment kinds')
        unique_together = ('name', 'organization')
        ordering = ('name',)


class Client(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Full name'))
    legal_category = models.ForeignKey(LegalEntityCategory, verbose_name=_('Legal entity category'), on_delete=models.PROTECT)
    tax_id = models.CharField(max_length=30, verbose_name=_('Tax ID'))
    market = models.ForeignKey(Market, verbose_name=_('Market'), on_delete=models.PROTECT)
    country = models.ForeignKey(Country, verbose_name=_('Country'), default=158, on_delete=models.PROTECT)
    state = models.ForeignKey(Region, verbose_name=_('State'), on_delete=models.PROTECT)
    city = models.ForeignKey(City, verbose_name=_('City'), on_delete=models.PROTECT)
    district = models.CharField(max_length=255, verbose_name=_('District'), null=True, blank=True)
    neighborhood = models.CharField(max_length=255, verbose_name=_('Neighborhood'), null=True, blank=True)
    postal_code = models.CharField(max_length=10, verbose_name=_('Postal code'))
    address = models.CharField(max_length=255, verbose_name=_('Address'), null=True, blank=True)
    ext_number = models.CharField(max_length=10, verbose_name=_('External number'), null=True, blank=True)
    int_number = models.CharField(max_length=10, verbose_name=_('Internal number'), null=True, blank=True)
    phone = models.CharField(max_length=15, verbose_name=_('Phone number'), null=True, blank=True)
    email = models.EmailField()
    fda = models.CharField(max_length=20, verbose_name=_('FDA'), null=True, blank=True)

    swift = models.CharField(max_length=20, verbose_name=_('SWIFT'), null=True, blank=True)
    aba = models.CharField(max_length=20, verbose_name=_('ABA'), null=True, blank=True)
    clabe = models.CharField(max_length=18, verbose_name=_('CLABE'), null=True, blank=True)
    payment_kind = models.ForeignKey(PaymentKind, verbose_name=_('Payment kind'), on_delete=models.PROTECT)
    max_money_credit_limit = models.FloatField(verbose_name=_('Max money credit limit'), null=True, blank=True)
    max_days_credit_limit = models.FloatField(verbose_name=_('Max days credit limit'), null=True, blank=True)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Client')
        verbose_name_plural = _('Clients')


class VehicleOwnershipKind(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Vehicle ownership kind')
        verbose_name_plural = _('Vehicle ownership kinds')
        unique_together = ('name', 'organization')


class VehicleKind(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Vehicle kind')
        verbose_name_plural = _('Vehicle kinds')
        unique_together = ('name', 'organization')


class VehicleFuelKind(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Vehicle fuel kind')
        verbose_name_plural = _('Vehicle fuel kinds')
        unique_together = ('name', 'organization')


class Vehicle(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    model = models.CharField(max_length=4, verbose_name=_('Model'), choices=vehicle_year_choices(), validators=[vehicle_validate_year])
    license_plate = models.CharField(max_length=15, verbose_name=_('License plate'))
    serial_number = models.CharField(max_length=100, verbose_name=_('Serial number'))
    color = models.CharField(max_length=50, verbose_name=_('Color'))
    ownership = models.ForeignKey(VehicleOwnershipKind, verbose_name=_('Ownership kind'), on_delete=models.PROTECT)
    fuel = models.ForeignKey(VehicleFuelKind, verbose_name=_('Fuel kind'), on_delete=models.PROTECT)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'),)
    comments = models.CharField(max_length=250, verbose_name=_('Comments'), blank=True, null=True)
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
    name = models.CharField(max_length=255, verbose_name=_('Full name'))
    population_registry_code = models.CharField(max_length=20, verbose_name=_('Population registry code'))
    tax_registry_code = models.CharField(max_length=20, verbose_name=_('Tax registry code'))
    social_number_code = models.CharField(max_length=20, verbose_name=_('Social number code'))
    birthday = models.DateField(verbose_name=_('Birthday'))
    sex = models.CharField(max_length=1, choices=[('', _('Sex')), ('M', _('Male')), ('F', _('Female'))])
    country = models.ForeignKey(Country, verbose_name=_('Country'), default=158, on_delete=models.PROTECT)
    state = models.ForeignKey(Region, verbose_name=_('State'), on_delete=models.PROTECT)
    city = models.ForeignKey(City, verbose_name=_('City'), on_delete=models.PROTECT)
    district = models.CharField(max_length=255, verbose_name=_('District'), null=True, blank=True)
    neighborhood = models.CharField(max_length=255, verbose_name=_('Neighborhood'), null=True, blank=True)
    postal_code = models.CharField(max_length=10, verbose_name=_('Postal code'))
    address = models.CharField(max_length=255, verbose_name=_('Address'), null=True, blank=True)
    ext_number = models.CharField(max_length=10, verbose_name=_('External number'), null=True, blank=True)
    int_number = models.CharField(max_length=10, verbose_name=_('Internal number'), null=True, blank=True)
    phone = models.CharField(max_length=15, verbose_name=_('Phone number'), null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT)
    is_maquilador = models.BooleanField(default=False, verbose_name=_('Is maquilador'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Collector')
        verbose_name_plural = _('Collectors')


class Maquilador(models.Model):
    zone = models.CharField(max_length=200, verbose_name=_('Zone'))
    name = models.CharField(max_length=255, verbose_name=_('Full name'))
    population_registry_code = models.CharField(max_length=20, verbose_name=_('Population registry code'))
    tax_registry_code = models.CharField(max_length=20, verbose_name=_('Tax registry code'))
    social_number_code = models.CharField(max_length=20, verbose_name=_('Social number code'))
    birthday = models.DateField(verbose_name=_('Birthday'))
    sex = models.CharField(max_length=1, choices=[('', _('Sex')), ('M', _('Male')), ('F', _('Female'))])
    country = models.ForeignKey(Country, verbose_name=_('Country'), default=158, on_delete=models.PROTECT)
    state = models.ForeignKey(Region, verbose_name=_('State'), on_delete=models.PROTECT)
    city = models.ForeignKey(City, verbose_name=_('City'), on_delete=models.PROTECT)
    district = models.CharField(max_length=255, verbose_name=_('District'), null=True, blank=True)
    neighborhood = models.CharField(max_length=255, verbose_name=_('Neighborhood'), null=True, blank=True)
    postal_code = models.CharField(max_length=10, verbose_name=_('Postal code'))
    address = models.CharField(max_length=255, verbose_name=_('Address'), null=True, blank=True)
    ext_number = models.CharField(max_length=10, verbose_name=_('External number'), null=True, blank=True)
    int_number = models.CharField(max_length=10, verbose_name=_('Internal number'), null=True, blank=True)
    phone = models.CharField(max_length=15, verbose_name=_('Phone number'), null=True, blank=True)
    email = models.EmailField()
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Maquilador')
        verbose_name_plural = _('Maquiladores')


class CollectorClient(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Full name'))
    legal_category = models.ForeignKey(LegalEntityCategory, verbose_name=_('Legal entity category'), on_delete=models.PROTECT)
    tax_id = models.CharField(max_length=30, verbose_name=_('Tax ID'))
    market = models.ForeignKey(Market, verbose_name=_('Market'), on_delete=models.PROTECT)
    country = models.ForeignKey(Country, verbose_name=_('Country'), default=158, on_delete=models.PROTECT)
    state = models.ForeignKey(Region, verbose_name=_('State'), on_delete=models.PROTECT)
    city = models.ForeignKey(City, verbose_name=_('City'), on_delete=models.PROTECT)
    district = models.CharField(max_length=255, verbose_name=_('District'), null=True, blank=True)
    neighborhood = models.CharField(max_length=255, verbose_name=_('Neighborhood'), null=True, blank=True)
    postal_code = models.CharField(max_length=10, verbose_name=_('Postal code'))
    address = models.CharField(max_length=255, verbose_name=_('Address'), null=True, blank=True)
    ext_number = models.CharField(max_length=10, verbose_name=_('External number'), null=True, blank=True)
    int_number = models.CharField(max_length=10, verbose_name=_('Internal number'), null=True, blank=True)
    phone = models.CharField(max_length=15, verbose_name=_('Phone number'), null=True, blank=True)
    email = models.EmailField()
    swift = models.CharField(max_length=20, verbose_name=_('SWIFT'), null=True, blank=True)
    aba = models.CharField(max_length=20, verbose_name=_('ABA'), null=True, blank=True)
    clabe = models.CharField(max_length=18, verbose_name=_('CLABE'), null=True, blank=True)
    payment_kind = models.ForeignKey(PaymentKind, verbose_name=_('Payment kind'), on_delete=models.PROTECT)
    max_money_credit_limit = models.FloatField(verbose_name=_('Max money credit limit'), null=True, blank=True)
    max_days_credit_limit = models.FloatField(verbose_name=_('Max days credit limit'), null=True, blank=True)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    collector = models.ForeignKey(Collector, verbose_name=_('Collector'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Collector client')
        verbose_name_plural = _('Collector clients')


class MaquiladorClient(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Full name'))
    legal_category = models.ForeignKey(LegalEntityCategory, verbose_name=_('Legal entity category'), on_delete=models.PROTECT)
    tax_id = models.CharField(max_length=30, verbose_name=_('Tax ID'))
    market = models.ForeignKey(Market, verbose_name=_('Market'), on_delete=models.PROTECT)
    country = models.ForeignKey(Country, verbose_name=_('Country'), default=158, on_delete=models.PROTECT)
    state = models.ForeignKey(Region, verbose_name=_('State'), on_delete=models.PROTECT)
    city = models.ForeignKey(City, verbose_name=_('City'), on_delete=models.PROTECT)
    district = models.CharField(max_length=255, verbose_name=_('District'), null=True, blank=True)
    neighborhood = models.CharField(max_length=255, verbose_name=_('Neighborhood'), null=True, blank=True)
    postal_code = models.CharField(max_length=10, verbose_name=_('Postal code'))
    address = models.CharField(max_length=255, verbose_name=_('Address'), null=True, blank=True)
    ext_number = models.CharField(max_length=10, verbose_name=_('External number'), null=True, blank=True)
    int_number = models.CharField(max_length=10, verbose_name=_('Internal number'), null=True, blank=True)
    phone = models.CharField(max_length=15, verbose_name=_('Phone number'), null=True, blank=True)
    email = models.EmailField()
    swift = models.CharField(max_length=20, verbose_name=_('SWIFT'), null=True, blank=True)
    aba = models.CharField(max_length=20, verbose_name=_('ABA'), null=True, blank=True)
    clabe = models.CharField(max_length=18, verbose_name=_('CLABE'), null=True, blank=True)
    payment_kind = models.ForeignKey(PaymentKind, verbose_name=_('Payment kind'), on_delete=models.PROTECT)
    max_money_credit_limit = models.FloatField(verbose_name=_('Max money credit limit'), null=True, blank=True)
    max_days_credit_limit = models.FloatField(verbose_name=_('Max days credit limit'), null=True, blank=True)
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    maquilador = models.ForeignKey(Maquilador, verbose_name=_('Maquilador'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Maquilador client')
        verbose_name_plural = _('Maquilador clients')


class OrchardProductClassification(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Description'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Product Classification')
        verbose_name_plural = _('Product Classifications')
        unique_together = ('name', 'organization')


class Orchard(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    producer = models.ForeignKey(ProductProducer, verbose_name=_('Producer'), on_delete=models.PROTECT)
    registration_date = models.DateField(verbose_name=_('Registration date'))
    forest_land_use_change = models.CharField(max_length=100, verbose_name=_('Forest land use change'), null=True, blank=True)
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
        verbose_name = _('Orchard certification kind')
        verbose_name_plural = _('Orchard certification kinds')
        unique_together = ('name', 'organization')
        ordering = ('name',)


class OrchardCertificationVerifier(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Orchard certification verifier')
        verbose_name_plural = _('Orchard certification verifiers')
        unique_together = ('name', 'organization')
        ordering = ('name',)


class OrchardCertification(models.Model):
    certification_kind = models.ForeignKey(OrchardCertificationKind, verbose_name=_('Orchard certification kind'), on_delete=models.PROTECT)
    certification_number = models.CharField(max_length=100, verbose_name=_('Certification number'))
    expiration_date = models.DateField(verbose_name=_('Expiration date'))
    verifier = models.ForeignKey(OrchardCertificationVerifier, verbose_name=_('Orchard certification verifier'), on_delete=models.PROTECT)
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
    related_supply = models.ForeignKey('self', verbose_name=_('Related supply'), null=True, blank=True, on_delete=models.SET_NULL, related_name='related_supplies')
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
    product_variety_size = models.ForeignKey(ProductVarietySize, verbose_name=_('Product variety size'), on_delete=models.PROTECT)
    mesh_bags_per_box = models.PositiveIntegerField(verbose_name=_('Mesh bags per box'))
    pieces_per_mesh_bag = models.PositiveIntegerField(verbose_name=_('Pieces per mesh bags'))
    mesh_bag_kind = models.ForeignKey(MeshBagKind, verbose_name=_('Mesh bag kind'), on_delete=models.PROTECT)
    mesh_bag_film_kind = models.ForeignKey(MeshBagFilmKind, verbose_name=_('Mesh bag film kind'), on_delete=models.PROTECT)
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
    box_kind = models.ForeignKey(BoxKind, verbose_name=_('Box kind'), on_delete=models.PROTECT)  # TODO: detallar tipos de caja por tipo de producto?
    product_variety = models.ForeignKey(ProductVariety, verbose_name=_('Product variety'), on_delete=models.PROTECT)
    product_variety_size = models.ForeignKey(ProductVarietySize, verbose_name=_('Product variety size'), on_delete=models.PROTECT)
    kg_per_box = models.FloatField(verbose_name=_('Kg per box'))
    supply = models.ForeignKey(Supply, verbose_name=_('Supply'), on_delete=models.PROTECT, related_name='product_packaging_supplies')
    is_dark = models.BooleanField(default=False, verbose_name=_('Is dark'))
    provisional_cost = models.FloatField(verbose_name=_('provisional cost'))
    provisional_price = models.FloatField(verbose_name=_('provisional price'))
    market_class = models.ForeignKey(MarketClass, verbose_name=_('Market class'), on_delete=models.PROTECT)
    supply_tray = models.ForeignKey(Supply, verbose_name=_('Supply tray'), on_delete=models.PROTECT, related_name='product_packaging_supplies_trays')
    # TODO: agregar campo para tipo de malla, o no se que va aquí pero falta uno
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Product Packaging')
        verbose_name_plural = _('Product Packaging')
        unique_together = ('name', 'organization')

