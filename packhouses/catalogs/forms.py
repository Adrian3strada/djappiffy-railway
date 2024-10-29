from django import forms
from .models import Product, ProductVarietySize, MarketStandardProductSize
from django.utils.translation import gettext_lazy as _
from django.forms.widgets import RadioSelect


class ProductVarietySizeForm(forms.ModelForm):
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        required=True,
        label=_('Product'),
    )

    market_standard_product_size = forms.ModelChoiceField(
        queryset=MarketStandardProductSize.objects.none(),
        required=False,
        label=_('Market Standard Product Sizes'),
        help_text=_(
            'Choose a Standard Product Size per Market (optional), it will put its name in the size name field.'),
        widget=forms.Select(attrs={'readonly': 'readonly'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.variety:
            self.fields['product'].initial = self.instance.variety.product

    class Meta:
        model = ProductVarietySize
        fields = ['product', 'variety', 'market', 'market_standard_product_size', 'name', 'alias', 'quality_kind', 'harvest_kind',
                  'description', 'product_kind', 'requires_corner_protector', 'is_enabled', 'order']
        widgets = {
            # 'product_kind': RadioSelect(),  # Usa RadioSelect para el campo ForeignKey
        }


class ProductVarietySizeInlineForm(forms.ModelForm):
    market_standard_product_size = forms.ModelChoiceField(
        queryset=MarketStandardProductSize.objects.none(),
        required=False,
        label=_('Market Standard Product Sizes'),
        help_text=_(
            'Choose a Standard Product Size per Market (optional), it will put its name in the size name field.'),
        widget=forms.Select(attrs={'readonly': 'readonly'})
    )

    class Meta:
        model = ProductVarietySize
        fields = ['market', 'market_standard_product_size', 'name', 'alias', 'quality_kind', 'harvest_kind',
                  'description', 'product_kind', 'requires_corner_protector', 'is_enabled', 'order']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'market' in self.data:
            try:
                market_id = int(self.data.get('market'))
                self.fields['market_standard_product_size'].queryset = MarketStandardProductSize.objects.filter(
                    market_id=market_id)
                if MarketStandardProductSize.objects.filter(name=self.name, market_id=market_id).exists():
                    self.fields['market_standard_product_size'].initial = MarketStandardProductSize.objects.get(
                        name=self.name, market_id=market_id)
            except (ValueError, TypeError) as e:
                print(e)
        elif self.instance.pk and self.instance.market:
            self.fields['market_standard_product_size'].queryset = MarketStandardProductSize.objects.filter(
                market=self.instance.market)
            if MarketStandardProductSize.objects.filter(name=self.instance.name, market=self.instance.market).exists():
                self.fields['market_standard_product_size'].initial = MarketStandardProductSize.objects.get(
                    name=self.instance.name, market=self.instance.market)

    class Media:
        js = ('js/admin/forms/product_variety_size.js',)
