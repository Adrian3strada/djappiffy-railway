from modeltranslation.translator import register, TranslationOptions
from .models import ProductKind, Incoterm, LocalDelivery, Currency


@register(ProductKind)
class ProductTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Incoterm)
class IncotermTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(LocalDelivery)
class LocalDeliveryTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(Currency)
class CurrencyTranslationOptions(TranslationOptions):
    fields = ('name',)
