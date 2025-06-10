from django.contrib import admin
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from packhouses.members.utils import (get_order_block, get_scheduleharvest_block, get_incomingproduct_block, 
                                        get_batch_block, get_foodsafety_block, get_certification_block, get_requisition_block,
                                        get_service_block, get_purchase_block, get_adjustment_block, get_storehouse_block
                                    )
from django.urls import reverse

@method_decorator(never_cache, name='dispatch')
def custom_index(self, request, extra_context=None):
    app_list = self.get_app_list(request)
    organization = request.organization.id
    blocks = []

    if request.user.has_perm("sales.view_order"):
        changelist_url = reverse("admin:sales_order_changelist")

        blocks.append(get_order_block("Orders(Ready)", "ready", organization, changelist_url))
        blocks.append(get_order_block("Orders(Open)", "open", organization, changelist_url))

    if request.user.has_perm("gathering.view_scheduleharvest"):
        changelist_url = reverse("admin:gathering_scheduleharvest_changelist")

        blocks.append(get_scheduleharvest_block("Schedule Harvest(Open)", "open", organization, changelist_url))
        blocks.append(get_scheduleharvest_block("Schedule Harvest(Ready)", "ready", organization, changelist_url))

    if request.user.has_perm("receiving.view_incomingproduct"):
        changelist_url = reverse("admin:receiving_incomingproduct_changelist")

        blocks.append(get_incomingproduct_block("Incoming Product(Open)", "open", None, organization, changelist_url))
        blocks.append(get_incomingproduct_block("Incoming Product(Ready)", "ready", False, organization, changelist_url))
        blocks.append(get_incomingproduct_block("Incoming Product(In quarantined)", "ready", True, organization, changelist_url))

    if request.user.has_perm("receiving.view_batch"):
        changelist_url = reverse("admin:receiving_batch_changelist")

        blocks.append(get_batch_block("Batch(Open)", "open", None, organization, changelist_url))
        blocks.append(get_batch_block("Batch(Ready)", "ready", False, organization, changelist_url))
        blocks.append(get_batch_block("Batch(For processing)", "ready", True, organization, changelist_url))

    if request.user.has_perm("receiving.view_foodsafety"):
        changelist_url = reverse("admin:receiving_foodsafety_changelist")
        blocks.append(get_foodsafety_block("Food Safety(Open)", "open", organization, changelist_url))
        blocks.append(get_foodsafety_block("Food Safety(Closed)", "closed", organization, changelist_url))

    if request.user.has_perm("certifications.view_certification"):
        changelist_url = reverse("admin:certifications_certification_changelist")
        blocks.append(get_certification_block("Certification(Expiration)", organization, changelist_url))
    
    if request.user.has_perm("purchases.view_requisition"):
        changelist_url = reverse("admin:purchases_requisition_changelist")
        blocks.append(get_requisition_block("Requisition", "ready", True, False, organization, changelist_url))
    
    if request.user.has_perm("purchases.view_serviceorder"):
        changelist_url = reverse("admin:purchases_serviceorder_changelist")
        blocks.append(get_service_block("Service Order(Created)", "open", "service", True, True, organization, changelist_url))
        blocks.append(get_service_block("Service Order(Paid)", "open", None, True, True, organization, changelist_url))
        blocks.append(get_service_block("Service Order(To be paid)", "open", None, False, True, organization, changelist_url))
    
    if request.user.has_perm("purchases.view_purchaseorder"):
        changelist_url = reverse("admin:purchases_purchaseorder_changelist")
        blocks.append(get_purchase_block("Purchase Order(Created)", "open", True, False, organization, changelist_url))
    
    if request.user.has_perm("storehouse.view_adjustmentinventory"):
        changelist_url = reverse("admin:storehouse_adjustmentinventory_changelist")
        blocks.append(get_adjustment_block("Adjustment Inventory(Inbound)", "inbound", organization, changelist_url))
        blocks.append(get_adjustment_block("Adjustment Inventory(Outbound)", "outbound", organization, changelist_url))

    if request.user.has_perm("storehouse.view_storehouseentry"):
        changelist_url = reverse("admin:storehouse_storehouseentry_changelist")
        blocks.append(get_storehouse_block("Storehouse Entry", organization, changelist_url))

    context = {
        **self.each_context(request),
        "title": self.index_title,
        "app_list": app_list,
        "widgets": blocks,
    }

    return TemplateResponse(request, "admin/index.html", context)

admin.site.index = custom_index.__get__(admin.site)