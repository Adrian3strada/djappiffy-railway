from django.forms import BaseInlineFormSet
from django import forms
from ..catalogs.models import SizePackaging
from .models import PackingPackage


class PackingPackageInlineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        instance = self.instance
        self.size_packaging_category = None  # Usamos esto también en clean()

        # --- 1. Lógica de campos readonly según status ---
        if instance.pk and instance.status != 'open':
            readonly_fields = [
                'batch', 'market', 'product_size', 'product_market_class',
                'product_ripeness', 'size_packaging', 'product_weight_per_packaging',
                'product_presentations_per_packaging', 'product_pieces_per_presentation',
                'packaging_quantity', 'processing_date',
            ]
            for field in readonly_fields:
                if field in self.fields:
                    self.fields[field].disabled = True
                    self.fields[field].required = False
                    self.fields[field].widget.attrs.update({'class': 'readonly-field', 'readonly': 'readonly'})

        # --- 2. Lógica de requeridos según size_packaging ---
        size_packaging = None

        # Caso 1: edición
        if instance.pk and instance.size_packaging_id:
            size_packaging = instance.size_packaging

        # Caso 2: viene del POST
        else:
            field_name = self.add_prefix("size_packaging")
            if field_name in self.data:
                try:
                    size_packaging_id = int(self.data.get(field_name))
                    size_packaging = SizePackaging.objects.filter(id=size_packaging_id).first()
                except (ValueError, TypeError):
                    pass

        # Aplicar reglas según categoría
        if size_packaging:
            self.size_packaging_category = size_packaging.category
            is_single = self.size_packaging_category == 'single'
            for f in ['product_presentations_per_packaging', 'product_pieces_per_presentation']:
                if f in self.fields:
                    self.fields[f].required = not is_single
                    if is_single:
                        self.fields[f].widget.attrs['placeholder'] = 'No requerido para "single"'
                    else:
                        self.fields[f].widget.attrs.pop('placeholder', None)

    def clean(self):
        cleaned = super().clean()

        # Aplicar lógica de solo lectura (sobrescribe cambios)
        if self.instance and self.instance.pk and self.instance.status != 'open':
            readonly_fields = [
                'batch', 'market', 'product_size', 'product_market_class',
                'product_ripeness', 'size_packaging', 'product_weight_per_packaging',
                'product_presentations_per_packaging', 'product_pieces_per_presentation',
                'packaging_quantity', 'processing_date',
            ]
            for field in readonly_fields:
                cleaned[field] = getattr(self.instance, field)

        return cleaned

    class Meta:
        model = PackingPackage
        fields = '__all__'



class PackingPackageInlineFormSet(BaseInlineFormSet):
    readonly_fields_if_not_open = [
        'batch', 'market', 'product_size', 'product_market_class',
        'product_ripeness', 'size_packaging', 'product_weight_per_packaging',
        'product_presentations_per_packaging', 'product_pieces_per_presentation',
        'packaging_quantity', 'processing_date',
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for form in self.forms:
            instance = form.instance

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
                    logger.debug("SizePackaging found: %s", size_packaging)
                    logger.debug("SizePackaging found: category %s", size_packaging.category)

                    if size_packaging.category == 'single':
                        logger.debug("SizePackaging category is 'single'")
                        form.fields['product_presentations_per_packaging'].required = False
                        form.fields['product_pieces_per_presentation'].required = False
                        form.data[f"{form.prefix}-product_presentations_per_packaging"] = None
                        form.data[f"{form.prefix}-product_pieces_per_presentation"] = None
                    else:
                        form.fields['product_presentations_per_packaging'].required = True
                        form.fields['product_pieces_per_presentation'].required = True

            if instance and instance.pk and instance.status not in ['open']:
                for field in self.readonly_fields_if_not_open:
                    if field in form.fields:
                        form.fields[field].disabled = True
                        form.fields[field].required = False
                        form.fields[field].widget.attrs.update({
                            'class': 'readonly-field',
                            'readonly': 'readonly'
                        })

                        if field in ['batch', 'market', 'product_size', 'product_market_class', 'product_ripeness',
                                     'size_packaging']:
                            form.fields[field].widget.can_add_related = False
                            form.fields[field].widget.can_change_related = False
                            form.fields[field].widget.can_delete_related = False
