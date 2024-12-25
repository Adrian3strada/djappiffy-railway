from modeltranslation.translator import register, TranslationOptions
from .models import TaxRegime, LegalEntityCategory, BillingSerieKind


"""
@register(TaxRegimeCategory)
class TaxRegimeCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)
"""


@register(TaxRegime)
class TaxRegimeTranslationOptions(TranslationOptions):
    fields = ('name',)


"""
@register(LegalEntityCategory)
class LegalEntityCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(BillingSerieKind)
class BillingSerieKindTranslationOptions(TranslationOptions):
    fields = ('name',)
"""
