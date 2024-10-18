from modeltranslation.translator import register, TranslationOptions
from .models import TaxRegimeCategory, TaxRegime


@register(TaxRegimeCategory)
class TaxRegimeCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(TaxRegime)
class TaxRegimeTranslationOptions(TranslationOptions):
    fields = ('name',)
