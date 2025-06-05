from modeltranslation.translator import register, TranslationOptions
from .models import (ProductKind, Incoterm, LocalDelivery, Currency, SupplyKind, SupplyMeasureUnitCategory,
                     FruitPurchasePriceCategory)


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


@register(SupplyKind)
class SupplyKindTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(SupplyMeasureUnitCategory)
class SupplyMeasureUnitCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(FruitPurchasePriceCategory)
class FruitPurchasePriceCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)

