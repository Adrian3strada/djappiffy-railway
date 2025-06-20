from django.contrib import admin
from .models import PackerEmployee, PackerLabel, PackingPackage, PackingPallet
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from .views import generate_label_pdf, generate_pending_label_pdf, discard_labels
from common.base.mixins import (ByOrganizationAdminMixin)
from packhouses.receiving.models import Batch
from packhouses.gathering.models import ScheduleHarvest
from packhouses.catalogs.models import (Market, Product, ProductSize, ProductMarketClass,
                                        ProductRipeness, SizePackaging, Pallet)
from .filters import (ByBatchForOrganizationPackingPackageFilter, ByMarketForOrganizationPackingPackageFilter,
                      ByProductSizeForOrganizationPackingPackageFilter)

# Register your models here.


@admin.register(PackerEmployee)
class PackerEmployeeAdmin(ByOrganizationAdminMixin):
    list_display = ("full_name", "new_labels", "pending_labels")
    search_fields = ("full_name",)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def new_labels(self, obj):
        return format_html(
            '<div style="display: flex; align-items: center; gap: 10px;">'
            '    <input type="number" id="number_of_labels_{}" name="quantity" value="10" min="1" max="1000" '
            '           style="width: 80px; text-align: center; background-color: #f8f9fa; border: 1px solid #ced4da;">'
            '    <button type="button" class="btn btn-primary" onclick="submitNewLabels({}, \'number_of_labels_{}\')">{}</button>'
            '</div>',
            obj.id, obj.id, obj.id, _("Generate")
        )

    new_labels.short_description = _("New labels")
    new_labels.allow_tags = True

    def pending_labels(self, obj):
        pending_count = PackerLabel.objects.filter(employee=obj, scanned_at__isnull=True).count()

        return format_html(
            '<div style="display: flex; align-items: center; gap: 10px;">'
            '    <input type="text" id="pending_quantity_{}" value="{}" readonly '
            '           style="width: 80px; text-align: center; background-color: #f8f9fa; border: 1px solid #ced4da;">'
            '    <button type="button" class="btn btn-primary" style="font-size: 14px;" onclick="submitPendingLabels({})">{}</button>'
            '    <button type="button" class="btn btn-danger" onclick="discardLabels({})">{}</button>'
            '</div>',
            obj.id,
            pending_count,
            obj.id,
            _("Download remaining"),
            obj.id,
            _("Discard")
        )

    pending_labels.short_description = _("Pending labels")
    pending_labels.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("generate_label/<int:employee_id>/", self.admin_site.admin_view(generate_label_pdf),
                 name="generate_label"),
            path("generate_pending_labels/<int:employee_id>/", self.admin_site.admin_view(generate_pending_label_pdf),
                 name="generate_pending_labels"),
            path("discard_labels/<int:employee_id>/", self.admin_site.admin_view(discard_labels),
                 name="discard_labels"),
        ]
        return custom_urls + urls

    class Media:
        js = ('js/admin/forms/packing/packer_label.js',)


class PackingPackageInline(admin.StackedInline):
    model = PackingPackage
    extra = 0
    fields = ('ooid', 'batch', 'market', 'product_size', 'product_market_class', 'product_ripeness',
              'size_packaging', 'product_weight_per_packaging', 'product_presentations_per_packaging',
              'product_pieces_per_presentation', 'packaging_quantity', 'processing_date', 'status')
    readonly_fields = ('ooid',)

    class Media:
        js = ('js/admin/forms/packing/packing_package_inline.js',)


@admin.register(PackingPallet)
class PackingPalletAdmin(ByOrganizationAdminMixin):
    list_display = ("ooid", "market", "get_product_sizes_display", "status")
    search_fields = ("ooid", )
    list_filter = ('product', 'market', "product_sizes", 'pallet', 'status')
    fields = ['ooid', 'product', 'market', 'product_sizes', 'pallet', 'status']
    inlines = [PackingPackageInline]

    def get_product_sizes_display(self, obj):
        return ", ".join([size.name for size in obj.product_sizes.all()]) if obj.product_sizes.exists() else "-"
    get_product_sizes_display.short_description = _("Product Sizes")
    get_product_sizes_display.admin_order_field = 'product_sizes__name'


    def get_readonly_fields(self, request, obj=None):
        fields = self.get_fields(request, obj)
        if obj and obj.status not in ['open']:
            return [f for f in fields if f != 'status']
        return ['ooid']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        organization = request.organization if hasattr(request, 'organization') else None

        if db_field.name == "product":
            kwargs["queryset"] = Product.objects.filter(organization=organization)

        if db_field.name == "market":
            kwargs["queryset"] = Market.objects.filter(organization=organization)

        if db_field.name == "pallet":
            kwargs["queryset"] = Pallet.objects.filter(product__organization=organization)
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda obj: f"{obj.name} (Q:{obj.max_packages_quantity})"
            return formfield

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        organization = request.organization if hasattr(request, 'organization') else None

        if db_field.name == "product_size":
            organization_products = Product.objects.filter(organization=organization)
            kwargs["queryset"] = ProductSize.objects.filter(product__in=organization_products)

        return super().formfield_for_manytomany(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/packing/packing_pallet.js',)


@admin.register(PackingPackage)
class PackingPackageAdmin(ByOrganizationAdminMixin):
    list_display = ("ooid", "batch", "market", "product_size", "product_market_class", "product_ripeness",
                    "size_packaging", "packaging_quantity", "processing_date", "packing_pallet", "status")
    search_fields = ("product_size__name",)
    list_filter = (ByBatchForOrganizationPackingPackageFilter, ByMarketForOrganizationPackingPackageFilter,
                   ByProductSizeForOrganizationPackingPackageFilter, "product_market_class", "product_ripeness", "size_packaging",
                   "processing_date", "packing_pallet", "status")
    fields = ['ooid', 'batch', 'market', 'product_size', 'product_market_class',
              'product_ripeness', 'size_packaging', 'product_weight_per_packaging',
              'product_presentations_per_packaging', 'product_pieces_per_presentation', 'packaging_quantity',
              'processing_date', 'packing_pallet', 'status']

    def get_readonly_fields(self, request, obj=None):
        fields = self.get_fields(request, obj)
        if obj and obj.status not in ['open']:
            return [f for f in fields if f != 'status']
        return ['ooid']

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        object_id = request.resolver_match.kwargs.get("object_id")
        obj = ProductSize.objects.get(id=object_id) if object_id else None
        organization = request.organization if hasattr(request, 'organization') else None
        size_packaging_instance = None

        if request.POST:
            size_packaging = request.POST.get("size_packaging")
            if size_packaging:
                size_packaging_instance = SizePackaging.objects.get(id=size_packaging)

        if db_field.name == "product_presentations_per_packaging":
            formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
            if size_packaging_instance:
                if size_packaging_instance.category == 'single':
                    formfield.required = False
            return formfield

        if db_field.name == "product_pieces_per_presentation":
            formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
            if size_packaging_instance:
                if size_packaging_instance.category == 'single':
                    formfield.required = False
            return formfield

        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        organization = request.organization if hasattr(request, 'organization') else None

        if db_field.name == "batch":
            kwargs["queryset"] = Batch.objects.filter(organization=organization)
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            return formfield

        if db_field.name == "market":
            kwargs["queryset"] = Market.objects.filter(organization=organization)

        if db_field.name == "product":
            kwargs["queryset"] = Product.objects.filter(organization=organization)

        if db_field.name == "product_size":
            organization_products = Product.objects.filter(organization=organization)
            kwargs["queryset"] = ProductSize.objects.filter(product__in=organization_products)

        if db_field.name == "product_market_class":
            organization_products = Product.objects.filter(organization=organization)
            kwargs["queryset"] = ProductMarketClass.objects.filter(product__in=organization_products)

        if db_field.name == "product_ripeness":
            organization_products = Product.objects.filter(organization=organization)
            kwargs["queryset"] = ProductRipeness.objects.filter(product__in=organization_products)

        if db_field.name == "size_packaging":
            kwargs["queryset"] = SizePackaging.objects.filter(organization=organization)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/packing/packing_package.js',)
