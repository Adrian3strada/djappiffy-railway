from django.contrib import admin
from .models import ProductKind

# Register your models here.


@admin.register(ProductKind)
class ProductKindAdmin(admin.ModelAdmin):
    pass
