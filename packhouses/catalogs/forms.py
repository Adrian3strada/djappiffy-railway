from django import forms
from .models import ProductVarietySize, MarketStandardProductSize
from django.utils.translation import gettext_lazy as _


class ProductVarietySizeForm(forms.ModelForm):
    market_standard_product_size = forms.ModelChoiceField(
        queryset=MarketStandardProductSize.objects.none(),
        required=False,
        label=_('Market Standard Product Sizes'),
        help_text=_('Choose a Standard Product Size per Market (optional), it will put its name in the size name field.'),
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
                self.fields['market_standard_product_size'].queryset = MarketStandardProductSize.objects.filter(market_id=market_id)
            except (ValueError, TypeError) as e:
                pass
        elif self.instance.pk and self.instance.market:
            self.fields['market_standard_product_size'].queryset = MarketStandardProductSize.objects.filter(market=self.instance.market)

