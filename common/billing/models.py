from django.db import models
from django.utils.timezone import localtime
from wagtail.models import Orderable
from organizations.models import Organization
from cities_light.models import City, Country, Region
from django.utils.translation import gettext_lazy as _
from common.base.models import LegalEntityCategory, CapitalFramework, Currency

# Create your models here.


class LegalEntity(Orderable):
    capital_framework = models.ForeignKey(CapitalFramework, verbose_name=_('Tax regime'), on_delete=models.PROTECT)
    name = models.CharField(max_length=255, verbose_name=_('Full name'))
    category = models.ForeignKey(LegalEntityCategory, verbose_name=_('Legal Entity Category'), on_delete=models.PROTECT)
    tax_id = models.CharField(max_length=30, verbose_name=_('Tax ID'))
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
    organization = models.OneToOneField(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Legal Entity')
        verbose_name_plural = _('Legal Entities')


class BillingSerieKind(models.Model):
    name = models.CharField(max_length=60, verbose_name=_('Name'), unique=True)

    def __str__(self):
        return f"{self.name}"


class BillingSerie(models.Model):
    serie = models.CharField(max_length=100, verbose_name=_('Serie'))
    folio = models.CharField(max_length=160, verbose_name=_('Folio'))
    kind = models.ForeignKey(BillingSerieKind, verbose_name=_('Kind'), on_delete=models.PROTECT)
    is_enabled = models.BooleanField(default=False, verbose_name=_('Is enabled'))
    legal_entity = models.ForeignKey(LegalEntity, verbose_name=_('Legal Entity'), on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Billing Serie')
        verbose_name_plural = _('Billing Series')
        unique_together = ('serie', 'folio', 'kind', 'legal_entity')

class ExchangeRate(models.Model):
    source_value = models.DecimalField(max_digits=10, decimal_places=2, default=1, editable=False)
    source = models.ForeignKey(Currency, verbose_name=_('Source'), related_name='exchange_rates_from', on_delete=models.PROTECT)
    exchange_rate_value = models.DecimalField(max_digits=10, verbose_name=_('Exchange Rate Value'), decimal_places=2)
    target = models.ForeignKey(Currency, verbose_name=_('Target'), related_name='exchange_rates_to', on_delete=models.PROTECT) 
    registration_date = models.DateTimeField(auto_now_add=True, verbose_name=_('Registration Date'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('Is enabled'))
    organization = models.ForeignKey(Organization, verbose_name=_('Organization'), on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Exchange Rate')
        verbose_name_plural = _('Exchange Rates')

    def composite_key(self):
        local_dt = localtime(self.registration_date)
        return f"{self.source.code}:{self.target.code} - {local_dt.strftime('%Y-%m-%d %H:%M')}"
    
    composite_key.short_description = 'Key'
    composite_key.admin_order_field = 'registration_date'

    def get_source_name(self):
        return self.source.name

    get_source_name.short_description = 'Source'
    get_source_name.admin_order_field = 'currency__name'

    def get_target_name(self):
        return self.target.name

    get_target_name.short_description = 'Target'
    get_target_name.admin_order_field = 'currency__name'
