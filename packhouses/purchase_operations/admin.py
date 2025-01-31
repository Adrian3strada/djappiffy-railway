from django.contrib import admin
from common.profiles.models import UserProfile
from .models import (Requisition, RequisitionSupply)
from packhouses.catalogs.models import Supply
from django.utils.translation import gettext_lazy as _
from common.base.decorators import uppercase_formset_charfield, uppercase_alphanumeric_formset_charfield
from common.base.decorators import uppercase_form_charfield, uppercase_alphanumeric_form_charfield
from common.base.mixins import (ByOrganizationAdminMixin, ByProductForOrganizationAdminMixin, DisableInlineRelatedLinksMixin,
                                ByUserAdminMixin, )
from django.core.exceptions import ObjectDoesNotExist
from .forms import RequisitionForm
from django.utils.html import format_html
from django.urls import reverse

# Register your models here.
class RequisitionSupplyInline(DisableInlineRelatedLinksMixin, admin.TabularInline):
    model = RequisitionSupply
    fields = ('supply', 'quantity', 'comments')
    extra = 0

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        parent_object_id = request.resolver_match.kwargs.get("object_id")
        try:
            parent_obj = Requisition.objects.get(id=parent_object_id) if parent_object_id else None
        except Requisition.DoesNotExist:
            parent_obj = None

        if db_field.name == "supply" and parent_obj:
            kwargs["queryset"] = Supply.objects.filter(
                organization=parent_obj.organization,
                is_enabled=True,
            )

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))

        # Obtener el objeto padre (Requisition)
        parent_object_id = request.resolver_match.kwargs.get("object_id")
        try:
            parent_obj = Requisition.objects.get(id=parent_object_id) if parent_object_id else None
        except Requisition.DoesNotExist:
            parent_obj = None

        # Si el estado del Requisition es 'closed', 'canceled' o 'ready', hacer todos los campos readonly
        if parent_obj and parent_obj.status in ['closed', 'canceled', 'ready']:
            readonly_fields.extend([
                field.name for field in self.model._meta.fields
                if field.name not in readonly_fields
            ])

        return readonly_fields

    def has_delete_permission(self, request, obj=None):
        # Obtener el objeto padre (Requisition)
        parent_object_id = request.resolver_match.kwargs.get("object_id")
        try:
            parent_obj = Requisition.objects.get(id=parent_object_id) if parent_object_id else None
        except Requisition.DoesNotExist:
            parent_obj = None

        # Si el estado del Requisition es 'closed', 'canceled' o 'ready', deshabilitar la eliminación
        if parent_obj and parent_obj.status in ['closed', 'canceled', 'ready']:
            return False

        return super().has_delete_permission(request, obj)

@admin.register(Requisition)
class RequisitionAdmin(ByOrganizationAdminMixin, ByUserAdminMixin):
    form = RequisitionForm
    fields = ('ooid', 'status',  'comments',)
    list_display = ('ooid', 'created_at', 'status', 'generate_actions_buttons')
    readonly_fields = ('ooid','status')
    inlines = (RequisitionSupplyInline,)

    def get_readonly_fields(self, request, obj=None):
        # Obtener los campos readonly predefinidos
        readonly_fields = list(super().get_readonly_fields(request, obj))

        # Campos siempre readonly cuando el objeto no existe
        if not obj:
            readonly_fields.append('ooid')

        # Campos readonly para objetos existentes
        if obj and obj.pk:
            readonly_fields.append('ooid')

        # Si el estado del corte está cerrado o cancelado, todos los campos son readonly
        if obj and obj.status in ['closed', 'canceled', 'ready']:
            # Filtrar solo los campos definidos en el admin que realmente existen
            readonly_fields.extend([
                field for field in self.fields if hasattr(obj, field)
            ])

        return readonly_fields

    def generate_actions_buttons(self, obj):
        requisition_pdf = reverse('requisition_pdf', args=[obj.pk])
        tooltip_requisition_pdf = _('Generate Requisition PDF')

        tooltip_ready = _('Send to Purchase Operations Departament')
        ready_url = reverse('set_requisition_ready', args=[obj.pk])
        confirm_ready_text = _('Are you sure you want to send this requisition to Purchase Operations Departament?')
        confirm_button_text = _('Yes, send')
        cancel_button_text = _('No')

        set_requisition_ready_button = ''
        if obj.status in ['open']:
            set_requisition_ready_button = format_html(
                '''
                <a class="button btn-ready-confirm" href="javascript:void(0);" data-toggle="tooltip" title="{}"
                   data-url="{}" data-message="{}" data-confirm="{}" data-cancel="{}" style="color:#4daf50;">
                    <i class="fa-solid fa-paper-plane"></i>
                </a>
                ''',
                tooltip_ready, ready_url, confirm_ready_text, confirm_button_text, cancel_button_text
            )

        return format_html(
            '''
            <a class="button" href="{}" target="_blank" data-toggle="tooltip" title="{}">
                <i class="fa-solid fa-print"></i>
            </a>
            {}
            ''',
            requisition_pdf, tooltip_requisition_pdf, set_requisition_ready_button
        )

    generate_actions_buttons.short_description = _('Actions')
    generate_actions_buttons.allow_tags = True

    class Media:
        js = ('js/admin/forms/packhouses/purchase_operations/requisition.js',)


