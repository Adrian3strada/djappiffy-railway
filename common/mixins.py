from django.db import models
from organizations.models import Organization
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


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

        if self.name:
            self.name = self.name.upper()

        if self.alias:
            self.alias = self.alias.upper()

        errors = {}

        try:
            super().clean()
        except ValidationError as e:
            errors = e.message_dict

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
        self.product_variety = getattr(self, 'product_variety', None)
        self.product_variety_id = getattr(self, 'product_variety_id', None)

        errors = {}

        try:
            super().clean()
        except ValidationError as e:
            errors = e.message_dict

        if self.product_variety_id:
            if self.__class__.objects.filter(name=self.name, product_variety=self.product_variety).exclude(pk=self.pk).exists():
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


class CleanNameAndProductProviderMixin(models.Model):
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


class CleanNameAndProductProducerMixin(models.Model):
    def __str__(self):
        return f"{self.name}"

    def clean(self):
        self.name = getattr(self, 'name', None)
        self.producer = getattr(self, 'producer', None)
        self.producer_id = getattr(self, 'producer_id', None)

        if self.name:
            self.name = self.name.upper()

        errors = {}

        try:
            super().clean()
        except ValidationError as e:
            errors = e.message_dict

        if self.producer_id:
            if self.__class__.objects.filter(name=self.name, producer=self.producer).exclude(pk=self.pk).exists():
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
        self.product_variety = getattr(self, 'product_variety', None)
        self.product_variety_id = getattr(self, 'product_variety_id', None)
        self.market = getattr(self, 'market', None)
        self.market_id = getattr(self, 'market_id', None)
        self.product_mass_volume_kind = getattr(self, 'product_mass_volume_kind', None)
        self.product_mass_volume_kind_id = getattr(self, 'product_mass_volume_kind_id', None)

        errors = {}

        try:
            super().clean()
        except ValidationError as e:
            errors = e.message_dict

        if self.product_variety_id and self.market_id and self.product_mass_volume_kind_id:
            if self.__class__.objects.filter(name=self.name, product_variety=self.product_variety, market=self.market,
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
