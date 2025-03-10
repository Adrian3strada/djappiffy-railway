from django.contrib import admin
from common.base.mixins import (
    ByOrganizationAdminMixin, ByProductForOrganizationAdminMixin,
    DisableInlineRelatedLinksMixin, ByUserAdminMixin
)
from .models import StorehouseEntry, StorehouseEntrySupply
from packhouses.purchase.models import PurchaseOrderSupply
from .forms import StorehouseEntrySupplyInlineFormSet

class StorehouseEntrySupplyInline(admin.StackedInline):
    model = StorehouseEntrySupply
    formset = StorehouseEntrySupplyInlineFormSet
    extra = 0
    can_delete = False


@admin.register(StorehouseEntry)
class StorehouseEntryAdmin(ByOrganizationAdminMixin):
    inlines = [StorehouseEntrySupplyInline]
    list_display = ('purchase_order', 'created_at', 'user')
    fields = ('purchase_order',)
    readonly_fields = ('created_at', 'user')

    def get_inline_instances(self, request, obj=None):
        inline_instances = super().get_inline_instances(request, obj)
        if obj and obj.purchase_order.status == "closed":
            for inline in inline_instances:
                inline.readonly_fields = inline.fields or [field.name for field in inline.model._meta.fields]
                inline.can_delete = False
                inline.extra = 0
        return inline_instances

    def get_readonly_fields(self, request, obj=None):
        ro_fields = list(self.readonly_fields)
        if obj and obj.purchase_order.status == "closed":
            ro_fields.append('purchase_order')
        return ro_fields

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for field in form.base_fields.values():
            widget = getattr(field, 'widget', None)
            if widget:
                widget.can_add_related = False
                widget.can_change_related = False
                widget.can_delete_related = False
                widget.can_view_related = False
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'purchase_order':
            kwargs['queryset'] = db_field.remote_field.model.objects.filter(status='ready')
            if hasattr(request, 'organization'):
                kwargs['queryset'] = kwargs['queryset'].filter(organization=request.organization)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        storehouse_entry = form.instance
        # Iteramos sobre una copia de la lista para evitar problemas al modificar el queryset
        for entry_supply in list(storehouse_entry.storehouseentrysupply_set.all()):
            pos = entry_supply.purchase_order_supply
            if entry_supply.received_quantity == 0 and entry_supply.inventoried_quantity == 0:
                entry_supply.delete()
                if not pos.storehouseentrysupply_set.exists():
                    pos.delete()
            else:
                if not pos.is_in_inventory:
                    pos.is_in_inventory = True
                    pos.save(update_fields=['is_in_inventory'])


    class Media:
        js = ('js/admin/forms/packhouses/storehouse/storehouse_entry.js',)
