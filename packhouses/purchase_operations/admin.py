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


@admin.register(Requisition)
class RequisitionAdmin(ByOrganizationAdminMixin, ByUserAdminMixin):
    form = RequisitionForm
    fields = ('ooid', 'comments',)
    list_display = ('ooid', 'user', 'created_at', 'status')
    readonly_fields = ('ooid',)
    inlines = (RequisitionSupplyInline,)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if not obj:
            readonly_fields.append('ooid')
        if obj and obj.pk:
            readonly_fields.append('ooid')

        return readonly_fields


