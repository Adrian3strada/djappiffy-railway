from django.forms import BaseInlineFormSet
from .models import ProductSize
from ..catalogs.models import SizePackaging


class PackingPackageInlineFormSet(BaseInlineFormSet):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for form in self.forms:
            if form.data and f"{form.prefix}-size_packaging" in form.data:
                try:
                    size_packaging_id = int(form.data.get(f"{form.prefix}-size_packaging"))
                except (ValueError, TypeError):
                    size_packaging_id = None
            else:
                size_packaging_id = None

            if size_packaging_id:
                size_packaging = SizePackaging.objects.filter(id=size_packaging_id).first()
                if size_packaging:
                    if size_packaging.category == 'single':
                        form.fields['product_presentations_per_packaging'].required = False
                        form.fields['product_pieces_per_presentation'].required = False
                        form.data[f"{form.prefix}-product_presentations_per_packaging"] = None
                        form.data[f"{form.prefix}-product_pieces_per_presentation"] = None
                    else:
                        form.fields['product_presentations_per_packaging'].required = True
                        form.fields['product_pieces_per_presentation'].required = True
