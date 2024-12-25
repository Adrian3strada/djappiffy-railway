from django import forms
from .models import Product, ProductVarietySize, MarketStandardProductSize, OrchardCertification
from django.forms import BaseInlineFormSet
from django.utils.translation import gettext_lazy as _


class ProductVarietySizeInlineForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['market_standard_size'].queryset = MarketStandardProductSize.objects.none()
        if self.instance and self.instance.pk:
            market = self.instance.market
            if market:
                self.fields['market_standard_size'].queryset = MarketStandardProductSize.objects.filter(market=market)
            else:
                self.fields['market_standard_size'].queryset = MarketStandardProductSize.objects.none()

    class Meta:
        model = ProductVarietySize
        fields = ['market', 'market_standard_size', 'name', 'alias', 'size_kind', 'harvest_kind',
                  'description', 'volume_kind', 'requires_corner_protector', 'is_enabled', 'order']

    class Media:
        js = ('js/admin/forms/catalogs/product_variety_size_inline.js',)


class ProductVarietySizeForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['market_standard_size'].queryset = MarketStandardProductSize.objects.none()
        if 'market' in self.data:
            try:
                market_id = int(self.data.get('market'))
                self.fields['market_standard_size'].queryset = MarketStandardProductSize.objects.filter(market_id=market_id, is_enabled=True)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['market_standard_size'].queryset = MarketStandardProductSize.objects.filter(market=self.instance.market, is_enabled=True)
        else:
            self.fields['market_standard_size'].queryset = MarketStandardProductSize.objects.none()

    class Meta:
        model = ProductVarietySize
        fields = '__all__'

    class Media:
        js = ('js/admin/forms/catalogs/product_variety_size.js',)


class ProductVarietyInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Itera sobre cada formulario en el formset
        for form in self.forms:
            instance = form.instance
            # Verifica si la instancia de ProductVariety está en uso
            if instance.pk and ProductVarietySize.objects.filter(variety=instance).exists():
                # Si está en uso, establece 'name' como readonly
                form.fields['name'].disabled = True
                form.fields['name'].widget.attrs.update({'readonly': 'readonly', 'disabled': 'disabled', 'class': 'readonly-field'})
                form.fields['DELETE'].initial = False
                form.fields['DELETE'].disabled = True
                form.fields['DELETE'].widget.attrs.update({'readonly': 'readonly', 'disabled': 'disabled', 'class': 'hidden'})


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
