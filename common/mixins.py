from django.db import models
from organizations.models import Organization
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
import os


# Create your mixins here.


class CleanKindAndOrganizationMixin(models.Model):
    def __str__(self):
        return f"{self.kind.name}"

    def clean(self):
        self.kind = getattr(self, 'kind', None)
        self.organization = getattr(self, 'organization', None)
        self.organization_id = getattr(self, 'organization_id', None)

        errors = {}

        try:
            super().clean()
        except ValidationError as e:
            errors = e.message_dict

        if self.organization_id:
            if self.__class__.objects.filter(kind=self.kind, organization=self.organization).exclude(pk=self.pk).exists():
                errors['kind'] = _('Kind must be unique, it already exists.')

        if errors:
            raise ValidationError(errors)

    class Meta:
        abstract = True



class CleanUniqueNameForOrganizationMixin(models.Model):
    def __str__(self):
        return f"{self.name}"

    def clean(self):
        self.name = getattr(self, 'name', None)
        self.organization = getattr(self, 'organization', None)
        self.organization_id = getattr(self, 'organization_id', None)

        errors = {}

        try:
            super().clean()
        except ValidationError as e:
            errors = e.message_dict

        if self.organization_id:
            if self.__class__.objects.filter(name=self.name, organization=self.organization).exclude(pk=self.pk).exists():
                errors['name'] = _('Name must be unique, it already exists.')

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True



class CleanNameAndOrganizationMixin(models.Model):
    def __str__(self):
        return f"{self.name}"

    def clean(self):
        self.name = getattr(self, 'name', None)
        self.organization = getattr(self, 'organization', None)
        self.organization_id = getattr(self, 'organization_id', None)

        if self.name:
            self.name = self.name.upper()

        errors = {}

        try:
            super().clean()
        except ValidationError as e:
            errors = e.message_dict

        if self.organization_id:
            if self.__class__.objects.filter(name=self.name, organization=self.organization).exclude(pk=self.pk).exists():
                errors['name'] = _('Name must be unique, it already exists.')

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class CleanNameAndCodeAndOrganizationMixin(models.Model):
    def __str__(self):
        return f"{self.name}"

    def clean(self):
        self.name = getattr(self, 'name', None)
        self.code = getattr(self, 'code', None)
        self.organization = getattr(self, 'organization', None)
        self.organization_id = getattr(self, 'organization_id', None)

        if self.name:
            self.name = self.name.upper()

        if self.code:
            self.code = self.code.upper()

        errors = {}

        try:
            super().clean()
        except ValidationError as e:
            errors = e.message_dict

        if self.organization_id:
            if self.__class__.objects.filter(name=self.name, organization=self.organization).exclude(pk=self.pk).exists():
                errors['name'] = _('Name must be unique, it already exists.')
            if self.__class__.objects.filter(code=self.code, organization=self.organization).exclude(pk=self.pk).exists():
                errors['code'] = _('Code must be unique, it already exists.')

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class CleanNameAndCategoryAndOrganizationMixin(models.Model):
    def __str__(self):
        return f"{self.name}"

    def clean(self):
        self.name = getattr(self, 'name', None)
        self.category = getattr(self, 'category', None)
        self.organization = getattr(self, 'organization', None)
        self.organization_id = getattr(self, 'organization_id', None)

        if self.name:
            self.name = self.name.upper()

        errors = {}

        try:
            super().clean()
        except ValidationError as e:
            errors = e.message_dict

        if self.organization_id:
            if self.__class__.objects.filter(name=self.name, category=self.category, organization=self.organization).exclude(
                pk=self.pk).exists():
                errors['name'] = _('Name and category must be unique, it already exists a registry with this data.')
                errors['category'] = _('Name and category must be unique, it already exists a registry with this data.')

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class CleanNameOrAliasAndOrganizationMixin(models.Model):
    def __str__(self):
        return f"{self.name}"

    def clean(self):
        self.name = getattr(self, 'name', None)
        self.alias = getattr(self, 'alias', None)
        self.organization = getattr(self, 'organization', None)
        self.organization_id = getattr(self, 'organization_id', None)

        if self.name:
            self.name = self.name.upper()

        if self.alias:
            self.alias = self.alias.upper()

        errors = {}

        try:
            super().clean()
        except ValidationError as e:
            errors = e.message_dict

        if self.organization_id:
            if self.__class__.objects.filter(name=self.name, organization=self.organization).exclude(pk=self.pk).exists():
                errors['name'] = _('Must be unique, it already exists.')
            if self.__class__.objects.filter(alias=self.alias, organization=self.organization).exclude(pk=self.pk).exists():
                errors['alias'] = _('Must be unique, it already exists.')

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class CleanNameAndMarketMixin(models.Model):
    def __str__(self):
        return f"{self.name}"

    def clean(self):
        self.name = getattr(self, 'name', None)
        self.market = getattr(self, 'market', None)
        self.market_id = getattr(self, 'market_id', None)

        if self.name:
            self.name = self.name.upper()

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
        abstract = True


class CleanNameAndAliasProductMixin(models.Model):
    def __str__(self):
        return f"{self.name}"

    def clean(self):
        self.name = getattr(self, 'name', None)
        self.alias = getattr(self, 'alias', None)
        self.product = getattr(self, 'product', None)
        self.product_id = getattr(self, 'product_id', None)

        if self.name:
            self.name = self.name.upper()

        if self.alias:
            self.alias = self.alias.upper()

        errors = {}

        try:
            super().clean()
        except ValidationError as e:
            errors = e.message_dict

        if self.product_id:
            if self.__class__.objects.filter(name=self.name, product=self.product).exclude(pk=self.pk).exists():
                errors['name'] = _('Name must be unique, it already exists.')
            if self.__class__.objects.filter(alias=self.alias, product=self.product).exclude(pk=self.pk).exists():
                errors['alias'] = _('Alias must be unique, it already exists.')

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class CleanProductMixin(models.Model):
    def __str__(self):
        return f"{self.name}"

    def clean(self):
        self.product = getattr(self, 'product', None)
        self.product_id = getattr(self, 'product_id', None)

        errors = {}

        try:
            super().clean()
        except ValidationError as e:
            errors = e.message_dict

        if self.product_id:
            if self.__class__.objects.filter(name=self.name, product=self.product).exclude(pk=self.pk).exists():
                errors['name'] = _('Name must be unique, it already exists.')

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class CleanProductVarietyMixin(models.Model):
    def __str__(self):
        return f"{self.name}"

    def clean(self):
        self.product_varieties = getattr(self, 'product_variety', None)
        self.product_variety_id = getattr(self, 'product_variety_id', None)

        errors = {}

        try:
            super().clean()
        except ValidationError as e:
            errors = e.message_dict

        if self.product_variety_id:
            if self.__class__.objects.filter(name=self.name, product_variety=self.product_varieties).exclude(pk=self.pk).exists():
                errors['name'] = _('Name must be unique, it already exists.')

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class CleanNameAndProductMixin(models.Model):
    def __str__(self):
        return f"{self.name}"

    def clean(self):
        self.name = getattr(self, 'name', None)
        self.product = getattr(self, 'product', None)
        self.product_id = getattr(self, 'product_id', None)

        if self.name:
            self.name = self.name.upper()

        errors = {}

        try:
            super().clean()
        except ValidationError as e:
            errors = e.message_dict

        if self.product_id:
            if self.__class__.objects.filter(name=self.name, product=self.product).exclude(pk=self.pk).exists():
                errors['name'] = _('Name must be unique, it already exists.')

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class CleanNameAndProviderMixin(models.Model):
    def __str__(self):
        return f"{self.name}"

    def clean(self):
        self.name = getattr(self, 'name', None)
        self.provider = getattr(self, 'provider', None)
        self.provider_id = getattr(self, 'provider_id', None)

        if self.name:
            self.name = self.name.upper()

        errors = {}

        try:
            super().clean()
        except ValidationError as e:
            errors = e.message_dict

        if self.provider_id:
            if self.__class__.objects.filter(name=self.name, provider=self.provider).exclude(pk=self.pk).exists():
                errors['name'] = _('Name must be unique, it already exists.')

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class CleanNameAndVarietyAndMarketAndVolumeKindMixin(models.Model):
    def __str__(self):
        return f"{self.name}"

    def clean(self):
        self.name = getattr(self, 'name', None)
        self.product_varieties = getattr(self, 'product_variety', None)
        self.product_variety_id = getattr(self, 'product_variety_id', None)
        self.markets = getattr(self, 'market', None)
        self.market_id = getattr(self, 'market_id', None)
        self.product_mass_volume_kind = getattr(self, 'product_mass_volume_kind', None)
        self.product_mass_volume_kind_id = getattr(self, 'product_mass_volume_kind_id', None)

        errors = {}

        try:
            super().clean()
        except ValidationError as e:
            errors = e.message_dict

        if self.product_variety_id and self.market_id and self.product_mass_volume_kind_id:
            if self.__class__.objects.filter(name=self.name, product_variety=self.product_varieties, market=self.markets,
                                             product_mass_volume_kind=self.product_mass_volume_kind).exclude(pk=self.pk).exists():
                errors['name'] = _('Name, variety, market and volume kind must be unique together.')
                errors['product_variety'] = _('Name, variety, market and volume kind must be unique together.')
                errors['market'] = _('Name, variety, market and volume kind must be unique together.')
                errors['product_mass_volume_kind'] = _('Name, variety, market and volume kind must be unique together.')

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class CleanNameAndMaquiladoraMixin(models.Model):
    def __str__(self):
        return f"{self.name}"

    def clean(self):
        self.name = getattr(self, 'name', None)
        self.maquiladora = getattr(self, 'maquiladora', None)
        self.maquiladora_id = getattr(self, 'maquiladora_id', None)

        if self.name:
            self.name = self.name.upper()

        errors = {}

        try:
            super().clean()
        except ValidationError as e:
            errors = e.message_dict

        if self.maquiladora_id:
            if self.__class__.objects.filter(name=self.name, maquiladora=self.maquiladora).exclude(pk=self.pk).exists():
                errors['name'] = _('Name must be unique, it already exists.')

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class IncotermsAndLocalDeliveryMarketMixin(models.Model):
    def clean(self):
        super().clean()

        market = getattr(self, 'market', None)
        if market:
            is_foreign = getattr(market, 'is_foreign', False)

            incoterms = getattr(self, 'incoterms', None)
            local_delivery = getattr(self, 'local_delivery', None)

            errors = {}

            # Verifica los campos según el valor de is_foreign
            if is_foreign:
                if not incoterms:
                    errors['incoterms'] = _('Incoterms is required when the market is foreign.')
                # Si es extranjero, asegúrate de que local_delivery sea None
                self.local_delivery = None
            else:
                if not local_delivery:
                    errors['local_delivery'] = _('Local delivery is required when the market is not foreign.')
                # Si no es extranjero, asegúrate de que incoterms sea None
                self.incoterms = None

            # Lanza errores de validación si es necesario
            if errors:
                raise ValidationError(errors)

    class Meta:
        abstract = True


class CleanNameAndServiceProviderAndOrganizationMixin(models.Model):
    def __str__(self):
        return f"{self.name}"

    def clean(self):
        self.name = getattr(self, 'name', None)
        self.service_provider = getattr(self, 'service_provider', None)
        self.service_provider_id = getattr(self, 'service_provider_id')
        self.organization = getattr(self, 'organization', None)
        self.organization_id = getattr(self, 'organization_id')

        if self.name:
            self.name = self.name.upper()

        errors = {}

        try:
            super().clean()
        except ValidationError as e:
            errors = e.message_dict

        if self.organization_id and self.service_provider_id:
            if self.__class__.objects.filter(name=self.name, service_provider=self.service_provider, organization=self.organization).exclude(pk=self.pk).exists():

                errors['name'] = _('Name and service provider must be unique together.')
                errors['service_provider'] = _('Name and service provider must be unique together.')

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True

class CleanDocumentsMixin(models.Model):
    def save(self, *args, **kwargs):
        try:
            old_instance = self.__class__.objects.get(pk=self.pk)
            if old_instance.route and old_instance.route != self.route:
                if os.path.isfile(old_instance.route.path):
                    os.remove(old_instance.route.path)
        except self.__class__.DoesNotExist:
            pass 

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.route and os.path.isfile(self.route.path):
            os.remove(self.route.path)
        super().delete(*args, **kwargs)

    class Meta:
        abstract = True
