from modeltranslation.translator import register, TranslationOptions
from .models import ProductKind


@register(ProductKind)
class ProductTranslationOptions(TranslationOptions):
    fields = ('name',)
