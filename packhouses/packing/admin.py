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
from packhouses.catalogs.models import Market, Product, ProductPhenologyKind, ProductSize, ProductMarketClass, \
    ProductRipeness, ProductPackaging


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
        js = ('js/admin.js',)


@admin.register(PackingPallet)
class PackingPalletAdmin(ByOrganizationAdminMixin):
    list_display = ("ooid", "market", "product_market_class", "product_size", "product", "status")
    search_fields = ("product_market_class__name", "product_size__name")
    list_filter = ("product_market_class", "product_size")
    fields = ['ooid', 'market', 'product', 'product_size', 'product_phenology', 'product_market_class',
              'product_ripeness', 'product_packaging', 'product_packaging_pallet', 'status']

    def get_readonly_fields(self, request, obj=None):
        fields = self.get_fields(request, obj)
        if obj and obj.status not in ['open']:
            return [f for f in fields if f != 'status']
        return ['ooid']


@admin.register(PackingPackage)
class PackingPackageAdmin(ByOrganizationAdminMixin):
    list_display = ("ooid", "batch", "market", "product_market_class", "product_size", "product", "status")
    search_fields = ("product_market_class__name", "product_size__name")
    list_filter = ("product_market_class", "product_size")
    fields = ['ooid', 'batch', 'market', 'product', 'product_phenology', 'product_size', 'product_market_class',
              'product_ripeness', 'product_packaging', 'product_weight_per_packaging',
              'product_presentations_per_packaging', 'product_pieces_per_presentation', 'packaging_quantity',
              'processing_date', 'status', 'packing_pallet']

    def get_readonly_fields(self, request, obj=None):
        fields = self.get_fields(request, obj)
        if obj and obj.status not in ['open']:
            return [f for f in fields if f != 'status']
        return ['ooid']

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        object_id = request.resolver_match.kwargs.get("object_id")
        obj = ProductSize.objects.get(id=object_id) if object_id else None
        organization = request.organization if hasattr(request, 'organization') else None
        product_packaging_instance = None

        if request.POST:
            product_packaging = request.POST.get("product_packaging")
            if product_packaging:
                product_packaging_instance = ProductPackaging.objects.get(id=product_packaging)

        if db_field.name == "product_presentations_per_packaging":
            formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
            if product_packaging_instance:
                if product_packaging_instance.category == 'single':
                    formfield.required = False
            return formfield

        if db_field.name == "product_pieces_per_presentation":
            formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
            if product_packaging_instance:
                if product_packaging_instance.category == 'single':
                    formfield.required = False
            return formfield

        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        organization = request.organization if hasattr(request, 'organization') else None

        if db_field.name == "batch":
            kwargs["queryset"] = Batch.objects.filter(organization=organization)
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda \
                obj: f"{obj.ooid} :: {obj.harvest_product_provider} - {obj.incomingproduct.scheduleharvest.created_at.strftime('%Y-%m-%d')}"
            return formfield

        if db_field.name == "market":
            kwargs["queryset"] = Market.objects.filter(organization=organization)

        if db_field.name == "product":
            kwargs["queryset"] = Product.objects.filter(organization=organization)

        if db_field.name == "product_phenology":
            organization_products = Product.objects.filter(organization=organization)
            kwargs["queryset"] = ProductPhenologyKind.objects.filter(product__in=organization_products)

        if db_field.name == "product_size":
            organization_products = Product.objects.filter(organization=organization)
            kwargs["queryset"] = ProductSize.objects.filter(product__in=organization_products)

        if db_field.name == "product_market_class":
            organization_products = Product.objects.filter(organization=organization)
            kwargs["queryset"] = ProductMarketClass.objects.filter(product__in=organization_products)

        if db_field.name == "product_ripeness":
            organization_products = Product.objects.filter(organization=organization)
            kwargs["queryset"] = ProductRipeness.objects.filter(product__in=organization_products)

        if db_field.name == "product_packaging":
            kwargs["queryset"] = ProductPackaging.objects.filter(organization=organization)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/packing/packing_package.js',)
