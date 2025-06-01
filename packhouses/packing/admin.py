from django.contrib import admin
from .models import PackerEmployee, PackerLabel, PackingPackage
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from .views import generate_label_pdf, generate_pending_label_pdf, discard_labels
from common.base.mixins import (ByOrganizationAdminMixin)
from packhouses.receiving.models import Batch
from packhouses.gathering.models import ScheduleHarvest
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
            path("generate_label/<int:employee_id>/", self.admin_site.admin_view(generate_label_pdf), name="generate_label"),
            path("generate_pending_labels/<int:employee_id>/", self.admin_site.admin_view(generate_pending_label_pdf), name="generate_pending_labels"),
            path("discard_labels/<int:employee_id>/", self.admin_site.admin_view(discard_labels), name="discard_labels"),
        ]
        return custom_urls + urls

    class Media:
        js = ('js/admin.js',)


@admin.register(PackingPackage)
class PackingPackageAdmin(ByOrganizationAdminMixin):
    list_display = ("batch", "product_market_class", "product_size" )
    search_fields = ("product_market_class__name", "product_size__name")
    list_filter = ("product_market_class", "product_size")

    def get_fields(self, request, obj=None):
        fields = ['ooid'] + [field for field in super().get_fields(request, obj) if field not in ['created_at', 'organization', 'ooid']]
        return fields

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        readonly_fields += ('ooid',)
        if obj:
            return readonly_fields + ['batch', 'product_market_class', 'product_size']
        return readonly_fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        organization = request.organization if hasattr(request, 'organization') else None

        if db_field.name == "batch":
            kwargs["queryset"] = Batch.objects.filter(organization=organization)
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda obj: f"{obj.ooid} :: {obj.harvest_product_provider} - {obj.incomingproduct.scheduleharvest.created_at.strftime('%Y-%m-%d')}"
            return formfield

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/admin/forms/packing/packing_package.js',)
