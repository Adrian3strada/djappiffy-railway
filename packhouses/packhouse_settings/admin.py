from django.contrib import admin
from .models import Status, ProductQualityKind, ProductKind
from common.formwidgets import UppercaseTextInputWidget, UppercaseAlphanumericTextInputWidget, AutoGrowingTextareaWidget


# Register your models here.


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductQualityKind)
class ProductQualityKindAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_enabled')
    list_filter = ('is_enabled',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['name'].widget = UppercaseTextInputWidget()
        return form


@admin.register(ProductKind)
class ProductKindAdmin(admin.ModelAdmin):
    pass

