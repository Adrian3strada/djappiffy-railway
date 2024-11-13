from modeltranslation.translator import register, TranslationOptions
from .models import OrganizationKind


@register(OrganizationKind)
class OrganizationKindTranslationOptions(TranslationOptions):
    fields = ('name',)
