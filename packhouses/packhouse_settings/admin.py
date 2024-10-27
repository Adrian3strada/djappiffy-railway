from django.contrib import admin
from .models import Status, ProductKind, ProductStandardSize

# Register your models here.


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductKind)
class ProductKindAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductStandardSize)
class ProductStandardSizeAdmin(admin.ModelAdmin):
    pass
