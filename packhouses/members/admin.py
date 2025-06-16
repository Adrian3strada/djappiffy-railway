from django.contrib import admin
from .models import MemberWidget
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.contrib.admin.utils import get_model_from_relation
from packhouses.members.utils import (get_order_block, get_scheduleharvest_block, get_incomingproduct_block, 
                                        get_batch_block, get_foodsafety_block, get_certification_block, get_requisition_block,
                                        get_service_block, get_purchase_block, get_adjustment_block, get_storehouse_block
                                    )
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

@admin.register(MemberWidget)
class MemberWidgetAdmin(admin.ModelAdmin):
    change_list_template = "admin/content.html"

    def has_add_permission(self, request):
        return False

    def changelist_view(self, request, extra_context=None):
        return self.custom_index(request, extra_context)

    @method_decorator(never_cache, name='dispatch')
    def custom_index(self, request, extra_context=None):
        organization = request.organization.id
        sections = []

        changelist_url_order = reverse("admin:sales_order_changelist")
        sections.append({
            "section_name": _("Orders"),
            "blocks": [
                get_order_block("Ready", "ready", organization, changelist_url_order),
                get_order_block("Open", "open", organization, changelist_url_order),
                # get_order_block("Close", "closed", organization, changelist_url_order),
                get_order_block("Canceled", "canceled", organization, changelist_url_order),
            ]
        })

        changelist_url_scheduleharvest = reverse("admin:gathering_scheduleharvest_changelist")
        sections.append({
            "section_name": _("Schedule Harvests"),
            "blocks": [
                get_scheduleharvest_block("Open", "open", organization, changelist_url_scheduleharvest),
                get_scheduleharvest_block("Ready(Harvest date)", "ready", organization, changelist_url_scheduleharvest),
                get_scheduleharvest_block("Closed", "closed", organization, changelist_url_scheduleharvest),
                get_scheduleharvest_block("Canceled", "canceled", organization, changelist_url_scheduleharvest),
            ]
        })

        changelist_url_incomigproduct = reverse("admin:receiving_incomingproduct_changelist")
        sections.append({
            "section_name": _("Incoming Product"),
            "blocks": [
                get_incomingproduct_block("Open", "open", None, organization, changelist_url_incomigproduct),
                get_incomingproduct_block("Ready", "ready", False, organization, changelist_url_incomigproduct),
                get_incomingproduct_block("In quarantined", "ready", True, organization, changelist_url_incomigproduct),
                get_incomingproduct_block("Closed", "closed", None, organization, changelist_url_incomigproduct),
                get_incomingproduct_block("Canceled", "canceled", None, organization, changelist_url_incomigproduct),
            ]
        })

        changelist_url_batch = reverse("admin:receiving_batch_changelist")
        sections.append({
            "section_name": _("Batches"),
            "blocks": [
                get_batch_block("Open", "open", None, organization, changelist_url_batch),
                get_batch_block("Ready", "ready", False, organization, changelist_url_batch),
                get_batch_block("For processing", "ready", True, organization, changelist_url_batch),
                get_batch_block("Closed", "closed", None, organization, changelist_url_batch),
                get_batch_block("Canceled", "canceled", None, organization, changelist_url_batch),
            ]
        })

        changelist_url_foodsafety = reverse("admin:receiving_foodsafety_changelist")
        sections.append({   
            "section_name": _("Food Safeties"),
            "blocks": [
                get_foodsafety_block("Open", "open", organization, changelist_url_foodsafety),
                get_foodsafety_block("Closed", "closed", organization, changelist_url_foodsafety),
            ]
        })

        changelist_url_certification = reverse("admin:certifications_certification_changelist")
        sections.append({   
            "section_name": _("Certifications"),
            "blocks": [
                get_certification_block("Expiration", organization, changelist_url_certification),
            ]
        })

        changelist_url_requisition = reverse("admin:purchases_requisition_changelist")
        sections.append({   
            "section_name": _("Requisition"),
            "blocks": [
                get_requisition_block("Ready", "ready", True, False, organization, changelist_url_requisition),
            ]
        })

        changelist_url_serviceorder = reverse("admin:purchases_serviceorder_changelist")
        sections.append({   
            "section_name": _("Service Order"),
            "blocks": [
                get_service_block("Created", "open", "service", True, True, organization, changelist_url_serviceorder),
                get_service_block("Paid", "open", None, True, True, organization, changelist_url_serviceorder),
                get_service_block("To be paid", "open", None, False, True, organization, changelist_url_serviceorder),
            ]
        })

        changelist_url_purchaseorder = reverse("admin:purchases_purchaseorder_changelist")
        sections.append({   
            "section_name": _("Purchase Order"),
            "blocks": [
                get_purchase_block("Created", "open", True, False, organization, changelist_url_purchaseorder),
            ]
        })

        changelist_url_adjustmentinventory = reverse("admin:storehouse_adjustmentinventory_changelist")
        sections.append({   
            "section_name": _("Adjustment Inventory"),
            "blocks": [
                get_adjustment_block("Inbound", "inbound", organization, changelist_url_adjustmentinventory),
                get_adjustment_block("Outbound", "outbound", organization, changelist_url_adjustmentinventory),
            ]
        })

        changelist_url_storehouseentry = reverse("admin:storehouse_storehouseentry_changelist")
        sections.append({   
            "section_name": _("Storehouse Entry"),
            "blocks": [
                get_storehouse_block("Storehouse Entry", organization, changelist_url_storehouseentry),
            ]
        })

        context = self.admin_site.each_context(request)
        context.update({
            "sections": sections,
            "opts": self.model._meta,
            "has_view_permission": self.has_view_permission(request),
        })

        return TemplateResponse(request, "admin/content.html", context)