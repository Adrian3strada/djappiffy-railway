from django.contrib import admin
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
from .models import PackerEmployee, PackerLabel, PackingPackage, PackingPallet, UnpackingPallet, UnpackingBatch, UnpackingSupply
from .filters import (ByBatchForOrganizationPackingPackageFilter, ByMarketForOrganizationPackingPackageFilter,
                      ByProductSizeForOrganizationPackingPackageFilter,
                      ByProductMarketClassForOrganizationPackingPackageFilter,
                      ByProductRipenessForOrganizationPackingPackageFilter,
                      BySizePackagingForOrganizationPackingPackageFilter,
                      ByPackingPalletForOrganizationPackingPackageFilter, ByProductForOrganizationPackingPalletFilter,
                      ByMarketForOrganizationPackingPalletFilter, ByPalletForOrganizationPackingPalletFilter,
                      ByProductSizeForOrganizationPackingPalletFilter)
from common.utils import is_instance_used
from organizations.models import Organization
from .forms import PackingPackageInlineFormSet, PackingPackageInlineForm

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
              'product_pieces_per_presentation', 'packaging_quantity', 'processing_date')
    readonly_fields = ('ooid',)
    # formset = PackingPackageInlineFormSet
    form = PackingPackageInlineForm

    def save_model(self, request, obj, form, change):
        if not obj.organization:
            obj.organization = request.organization
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        parent_object_id = request.resolver_match.kwargs.get("object_id")
        try:
            parent_obj = PackingPackage.objects.get(id=parent_object_id) if parent_object_id else None
        except PackingPackage.DoesNotExist:
            parent_obj = None
        organization = request.organization if hasattr(request, 'organization') else None

        if db_field.name == "batch":
            kwargs["queryset"] = Batch.objects.filter(organization=organization, status='ready', parent__isnull=True)
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            return formfield

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/packing/packing_package_inline.js',)


@admin.register(PackingPallet)
class PackingPalletAdmin(ByOrganizationAdminMixin):
    list_display = ("ooid", "market", "get_product_sizes_display", "status", "get_action_buttons")
    search_fields = ("ooid",)
    list_filter = (ByProductForOrganizationPackingPalletFilter, ByMarketForOrganizationPackingPalletFilter,
                   ByProductSizeForOrganizationPackingPalletFilter, ByPalletForOrganizationPackingPalletFilter,
                   'status')
    fields = ['ooid', 'product', 'market', 'product_sizes', 'pallet', 'status']
    inlines = [PackingPackageInline]

    def get_action_buttons(self, obj):
        action_set_status_ready = format_html('''
                <a class="button btn-cancel-confirm" href="javascript:void(0);" data-toggle="tooltip" title="{}"
                data-url="{}" data-message="{}" data-confirm="{}" data-cancel="{}" style="color:#4daf50;">
                <i class="fa-solid fa-paper-plane"></i></a>''',_("Set ready"), 2,3,4,3,
            ) if obj.status == 'open' else ''
        action_unpack = format_html('''
                <a class="button btn-cancel-confirm" href="javascript:void(0);" data-toggle="tooltip" title="{}"
                data-url="{}" data-message="{}" data-confirm="{}" data-cancel="{}">
                <i class="fa-solid fa-box-open"></i></a>''',"iii", 2,3,4,3, _("Generate Label")
            ) if obj.status == 'canceled' else ''
        action_set_status_canceled = format_html('''
                <a class="button btn-cancel-confirm" href="javascript:void(0);" data-toggle="tooltip" title="{}"
                data-url="{}" data-message="{}" data-confirm="{}" data-cancel="{}" style="color:red;">
                <i class="fa fa-ban"></i></a>''',"iii", 2,3,4,3, _("Generate Label")
            ) if obj.status == 'ready' else ''
        action_delete = format_html('''
        <a class="button btn-cancel-confirm" href="javascript:void(0);" data-toggle="tooltip" title="{}"
        data-url="{}" data-message="{}" data-confirm="{}" data-cancel="{}" style="color:red;">
        <i class="fa fa-trash"></i></a>''', "iii", 2, 3, 4, 3, _("Generate Label")
        ) if obj.status == 'open' else ''

        return format_html(f"{action_set_status_ready} {action_unpack} {action_set_status_canceled} {action_delete}")

    get_action_buttons.short_description = _("Actions")

    def get_product_sizes_display(self, obj):
        return ", ".join([size.name for size in obj.product_sizes.all()]) if obj.product_sizes.exists() else "-"

    get_product_sizes_display.short_description = _("Product Sizes")
    get_product_sizes_display.admin_order_field = 'product_sizes__name'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and is_instance_used(obj, exclude=[Organization, Product, Market, ProductSize, Pallet]):
            form.base_fields['product'].widget.attrs.update({'class': 'readonly-field', 'readonly': 'readonly'})
            form.base_fields['market'].widget.attrs.update({'class': 'readonly-field', 'readonly': 'readonly'})
            form.base_fields['product_sizes'].widget.attrs.update({'class': 'readonly-field', 'readonly': 'readonly'})
            form.base_fields['pallet'].widget.attrs.update({'class': 'readonly-field', 'readonly': 'readonly'})
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ['ooid']
        if obj and obj.status not in ['open']:
            readonly_fields.extend(['status'])
        return readonly_fields

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        object_id = request.resolver_match.kwargs.get("object_id")
        obj = self.model.objects.filter(pk=object_id).first() if object_id else None
        organization = request.organization if hasattr(request, 'organization') else None

        if db_field.name == "status":
            choices = list(db_field.choices)
            if obj:
                if obj.status in ["open", "ready" "canceled"]:
                    # Solo mostrar open y ready
                    choices = [c for c in choices if c[0] in ["open", "ready", "canceled"]]
                else:
                    # Solo mostrar la opción actual
                    choices = [c for c in choices if c[0] == obj.status]
            else:
                # Si es nuevo, solo mostrar open y ready
                choices = [c for c in choices if c[0] in ["open", "ready"]]
            kwargs['choices'] = choices

        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        object_id = request.resolver_match.kwargs.get("object_id")
        obj = self.model.objects.filter(pk=object_id).first() if object_id else None
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
                   ByProductSizeForOrganizationPackingPackageFilter,
                   ByProductMarketClassForOrganizationPackingPackageFilter,
                   ByProductRipenessForOrganizationPackingPackageFilter,
                   BySizePackagingForOrganizationPackingPackageFilter,
                   "processing_date", ByPackingPalletForOrganizationPackingPackageFilter, "status")
    fields = ['ooid', 'batch', 'market', 'product_size', 'product_market_class',
              'product_ripeness', 'size_packaging', 'product_weight_per_packaging',
              'product_presentations_per_packaging', 'product_pieces_per_presentation', 'packaging_quantity',
              'processing_date', 'packing_pallet', 'status']

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ['ooid']
        if obj and obj.status in ['closed', 'cancelled']:
            readonly_fields = self.fields
        return readonly_fields

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        ready_disabeld_fields = ['batch', 'market', 'product_size', 'product_market_class', 'product_ripeness',
                                 'size_packaging', 'product_weight_per_packaging',
                                 'product_presentations_per_packaging', 'product_pieces_per_presentation',
                                 'packaging_quantity', 'processing_date'
                                 ]
        if obj and obj.status not in ['open']:
            for field in ready_disabeld_fields:
                if field in form.base_fields:
                    form.base_fields[field].widget.attrs.update({'class': 'readonly-field', 'readonly': 'readonly'})
        return form

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        object_id = request.resolver_match.kwargs.get("object_id")
        obj = PackingPackage.objects.get(id=object_id) if object_id else None
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

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        object_id = request.resolver_match.kwargs.get("object_id")
        obj = self.model.objects.filter(pk=object_id).first() if object_id else None
        organization = request.organization if hasattr(request, 'organization') else None

        if db_field.name == "status":
            choices = list(db_field.choices)
            if obj:
                if obj.status in ["open", "ready"]:
                    # Solo mostrar open y ready
                    choices = [c for c in choices if c[0] in ["open", "ready"]]
                else:
                    # Solo mostrar la opción actual
                    choices = [c for c in choices if c[0] == obj.status]
            else:
                # Si es nuevo, solo mostrar open y ready
                choices = [c for c in choices if c[0] in ["open", "ready"]]
            kwargs['choices'] = choices

        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        organization = request.organization if hasattr(request, 'organization') else None

        if db_field.name == "batch":
            kwargs["queryset"] = Batch.objects.filter(organization=organization, is_available_for_processing=True, parent__isnull=True)
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


class UnpackingBatchInline(admin.TabularInline):
    model = UnpackingBatch
    extra = 0
    fields = ('initial_weight', 'lost_weight', 'return_weight')


class UnpackingSupplyInline(admin.TabularInline):
    model = UnpackingSupply
    extra = 0
    fields = ('supply', 'initial_quantity', 'lost_quantity', 'return_quantity')


@admin.register(UnpackingPallet)
class UnpackingPalletAdmin(ByOrganizationAdminMixin):
    list_display = ("packing_pallet", "created_at")
    list_filter = ("packing_pallet", "created_at")
    fields = ['packing_pallet']
    inlines = [UnpackingBatchInline, UnpackingSupplyInline]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        organization = request.organization if hasattr(request, 'organization') else None

        if db_field.name == "packing_pallet":
            kwargs["queryset"] = PackingPallet.objects.filter(product__organization=organization)
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            return formfield

        return super().formfield_for_foreignkey(db_field, request, **kwargs)
