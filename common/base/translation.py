from modeltranslation.translator import register, TranslationOptions
from .models import ProductKind, Incoterm, LocalDelivery


@register(ProductKind)
class ProductTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Incoterm)
class IncotermTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(LocalDelivery)
class LocalDeliveryTranslationOptions(TranslationOptions):
    fields = ('name',)
