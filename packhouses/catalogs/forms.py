from django import forms
from .models import (
    Product, ProductSize, MarketStandardProductSize, OrchardCertification, HarvestingCrew,
    ProductHarvestSizeKind,
    HarvestingPaymentSetting
)
from django.forms import BaseInlineFormSet
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from common.utils import is_instance_used

class ProductVarietySizeInlineForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['market_standard_product_size'].queryset = MarketStandardProductSize.objects.none()
        if self.instance and self.instance.pk:
            market = self.instance.market
            if market:
                self.fields[
                    'market_standard_product_size'].queryset = MarketStandardProductSize.objects.filter(market=market)
            else:
                self.fields['market_standard_product_size'].queryset = MarketStandardProductSize.objects.none()

    class Meta:
        model = ProductSize
        fields = ['markets', 'market_standard_product_size', 'name', 'alias', 'product_size_kind',
                  'description', 'product_mass_volume_kind', 'requires_corner_protector', 'is_enabled', 'order']

    class Media:
        js = ('js/admin/forms/catalogs/product_variety_size_inline.js',)


class ProductVarietyInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for form in self.forms:
            instance = form.instance
            # Verifica si la instancia de ProductVariety está en uso
            if instance.pk and ProductSize.objects.filter(product_varieties=instance).exists():
                form.fields['name'].disabled = True
                form.fields['name'].widget.attrs.update(
                    {'readonly': 'readonly', 'disabled': 'disabled', 'class': 'readonly-field'})
                form.fields['DELETE'].initial = False
                form.fields['DELETE'].disabled = True
                form.fields['DELETE'].widget.attrs.update(
                    {'readonly': 'readonly', 'disabled': 'disabled', 'class': 'hidden'})


class ProductHarvestSizeKindInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for form in self.forms:
            instance = form.instance

            # Verifica si la instancia de ProductVariety está en uso
            if instance.pk and ProductSize.objects.filter(product_harvest_size_kind=instance).exists():
                form.fields['name'].disabled = True
                form.fields['name'].widget.attrs.update(
                    {'readonly': 'readonly', 'disabled': 'disabled', 'class': 'readonly-field'})
                form.fields['DELETE'].initial = False
                form.fields['DELETE'].disabled = True
                form.fields['DELETE'].widget.attrs.update(
                    {'readonly': 'readonly', 'disabled': 'disabled', 'class': 'hidden'})


class OrchardCertificationForm(forms.ModelForm):
    class Meta:
        model = OrchardCertification
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        certification_kind = cleaned_data.get('certification_kind')
        extra_code = cleaned_data.get('extra_code')

        if certification_kind and certification_kind.extra_code_name and not extra_code:
            raise forms.ValidationError({
                'extra_code': _('This field is required.')
            })

        return cleaned_data


class HarvestingCrewForm(forms.ModelForm):
    class Meta:
        model = HarvestingCrew
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data


class HarvestingPaymentSettingInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type_harvests = []

    def clean(self):
        # Llamamos al clean original
        super().clean()

        for form in self.forms:
            # Validamos que el formulario sea válido y que no esté marcado para eliminar
            if not form.is_valid() or form.cleaned_data.get('DELETE', False):
                continue

            type_harvest = form.cleaned_data.get('type_harvest')

            if type_harvest:
                # Verifica si ya existe el type_harvest en la lista
                if type_harvest in self.type_harvests:
                    raise forms.ValidationError({
                        'type_harvest': _(
                            f'Type harvest "{type_harvest}" is already selected. Only one of each type is allowed.')
                    })
                else:
                    self.type_harvests.append(type_harvest)

        # Lanza una validación general si hay errores
        if any(form.errors for form in self.forms):
            raise forms.ValidationError(
                _(f'Type harvest "{type_harvest}" is already selected. Only one of each type is allowed.')
            )
