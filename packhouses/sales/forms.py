from django.forms import BaseInlineFormSet
from .models import ProductSize
from ..catalogs.models import SizePackaging, ProductPackagingPallet


class OrderItemWeightFormSet(BaseInlineFormSet):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for form in self.forms:
            if form.data and f"{form.prefix}-product_size" in form.data:
                try:
                    product_size_id = int(form.data.get(f"{form.prefix}-product_size"))
                except (ValueError, TypeError):
                    product_size_id = None
            else:
                product_size_id = None

            if product_size_id:
                product_size = ProductSize.objects.filter(id=product_size_id).first()
                if product_size:
                    if product_size.category in ['mix', 'waste', 'biomass']:
                        form.fields['product_phenology'].required = False
                        form.fields['product_market_class'].required = False
                        form.fields['product_ripeness'].required = False
                        form.data[f"{form.prefix}-product_phenology"] = None
                        form.data[f"{form.prefix}-product_market_class"] = None
                    else:
                        form.fields['product_phenology'].required = True
                        form.fields['product_market_class'].required = True


class OrderItemPackagingFormSet(BaseInlineFormSet):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for form in self.forms:
            print("Processing form:", form.data)
            if form.data:
                if f"{form.prefix}-product_size" in form.data:
                    try:
                        product_size_id = int(form.data.get(f"{form.prefix}-product_size"))
                    except (ValueError, TypeError):
                        product_size_id = None
                else:
                    product_size_id = None

                if f"{form.prefix}-size_packaging" in form.data:
                    try:
                        size_packaging_id = int(form.data.get(f"{form.prefix}-size_packaging"))
                    except (ValueError, TypeError):
                        size_packaging_id = None
                else:
                    size_packaging_id = None

                if product_size_id:
                    product_size = ProductSize.objects.filter(id=product_size_id).first()
                    if product_size:
                        if product_size.category in ['mix', 'waste', 'biomass']:
                            form.fields['product_phenology'].required = False
                            form.fields['product_market_class'].required = False
                            form.data[f"{form.prefix}-product_phenology"] = None
                            form.data[f"{form.prefix}-product_market_class"] = None
                        else:
                            form.fields['product_phenology'].required = True
                            form.fields['product_market_class'].required = True

                if size_packaging_id:
                    size_packaging = SizePackaging.objects.filter(id=size_packaging_id).first()
                    if size_packaging:
                        if size_packaging.product_presentation:
                            form.fields['product_presentations_per_packaging'].required = True
                            form.fields['product_pieces_per_presentation'].required = True
                        else:
                            form.fields['product_presentations_per_packaging'].required = False
                            form.fields['product_pieces_per_presentation'].required = False
                            form.data[f"{form.prefix}-product_presentations_per_packaging"] = None
                            form.data[f"{form.prefix}-product_pieces_per_presentation"] = None


class OrderItemPalletFormSet(BaseInlineFormSet):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for form in self.forms:
            if form.data and f"{form.prefix}-product_size" in form.data:
                try:
                    product_size_id = int(form.data.get(f"{form.prefix}-product_size"))
                except (ValueError, TypeError):
                    product_size_id = None
            else:
                product_size_id = None

            if f"{form.prefix}-pallet" in form.data:
                try:
                    pallet_id = int(form.data.get(f"{form.prefix}-pallet"))
                except (ValueError, TypeError):
                    pallet_id = None
            else:
                pallet_id = None

            if product_size_id:
                product_size = ProductSize.objects.filter(id=product_size_id).first()
                if product_size:
                    if product_size.category in ['mix', 'waste', 'biomass']:
                        form.fields['product_phenology'].required = False
                        form.fields['product_market_class'].required = False
                        form.fields['product_ripeness'].required = False
                        form.data[f"{form.prefix}-product_phenology"] = None
                        form.data[f"{form.prefix}-product_market_class"] = None
                    else:
                        form.fields['product_phenology'].required = True
                        form.fields['product_market_class'].required = True

            if pallet_id:
                pallet = ProductPackagingPallet.objects.filter(id=pallet_id).first()
                if pallet:
                    if pallet.size_packaging.product_presentation:
                        form.fields['product_presentations_per_packaging'].required = True
                        form.fields['product_pieces_per_presentation'].required = True
                    else:
                        form.fields['product_presentations_per_packaging'].required = False
                        form.fields['product_pieces_per_presentation'].required = False
                        form.data[f"{form.prefix}-product_presentations_per_packaging"] = None
                        form.data[f"{form.prefix}-product_pieces_per_presentation"] = None
