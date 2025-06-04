from django.contrib import admin
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.utils.translation import gettext_lazy as _
from django.utils.http import urlencode
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import TruncDate

from packhouses.receiving.models import Batch, IncomingProduct
from packhouses.gathering.models import ScheduleHarvest
from packhouses.sales.models import Order

@method_decorator(never_cache, name='dispatch')
def custom_index(self, request, extra_context=None):
    app_list = self.get_app_list(request)

    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    next_week = today + timedelta(days=7)
    next_month = today + timedelta(days=30)

    context = {
        **self.each_context(request),
        "title": self.index_title,
        "app_list": app_list,
        "period": {
            "day_title": _('Today'),
            "week_ago_title": _('Last 7 days'),
            "month_ago_title": _('Last 30 days'),
            "next_week_title": _('Next 7 days'),
            "next_month_title": _('Next 30 days'),
        },
    }


    if request.user.has_perm("gathering.view_scheduleharvest"):

        changelist_url = reverse("admin:gathering_scheduleharvest_changelist")
        context["total_schedule_harvest"] = {
            "block_name": _('Schedule harvest'),
            "day": ScheduleHarvest.objects.filter(harvest_date=today, organization=request.organization).count(),
            "day_url": f"{changelist_url}?{urlencode({'harvest_date': today, 'organization__id': request.organization.id})}",
            "week": ScheduleHarvest.objects.filter(harvest_date__range=(today, next_week), organization=request.organization).count(),
            "week_url": f"{changelist_url}?{urlencode({'harvest_date__gte': today, 'harvest_date__lte': next_week, 'organization__id': request.organization.id})}",
            "month": ScheduleHarvest.objects.filter(harvest_date__range=(today, next_month), organization=request.organization).count(),
            "month_url": f"{changelist_url}?{urlencode({'harvest_date__gte': today, 'harvest_date__lte': next_month, 'organization__id': request.organization.id})}",
        }

    if request.user.has_perm("receiving.view_batch"):

        changelist_url = reverse("admin:receiving_batch_changelist")
        context["total_batch"] = {
            "block_name": _('Batch'),
            "day": Batch.objects.filter(created_at__date=today, organization=request.organization).count(),
            "day_url": f"{changelist_url}?{urlencode({'created_at__date': today, 'organization__id': request.organization.id})}",
            "week": Batch.objects.filter(created_at__date__gte=week_ago, organization=request.organization).count(),
            "week_url": f"{changelist_url}?{urlencode({'created_at__date__gte': week_ago, 'organization__id': request.organization.id})}",
            "month": Batch.objects.filter(created_at__date__gte=month_ago, organization=request.organization).count(),
            "month_url": f"{changelist_url}?{urlencode({'created_at__date__gte': month_ago, 'organization__id': request.organization.id})}",
        }

    if request.user.has_perm("receiving.view_incomingproduct"):

        changelist_url = reverse("admin:receiving_incomingproduct_changelist")
        context["incomingproduct"] = {
            "block_name": _('Incoming product'),
            "open_title": _('Open'),
            "open": IncomingProduct.objects.filter(status="open", organization=request.organization).count(),
            "open_url": f"{changelist_url}?{urlencode({'status': 'open', 'organization__id': request.organization.id})}",
            "quarantine_title": _('Quarantine'),
            "quarantine": IncomingProduct.objects.filter(status="open", is_quarantined=True, organization=request.organization).count(),
            "quarantine_url": f"{changelist_url}?{urlencode({'status':'open', 'is_quarantined':True, 'organization__id': request.organization.id})}",
        }

    if request.user.has_perm("sales.view_order"):

        changelist_url = reverse("admin:sales_order_changelist")
        context["order"] = {
            "block_name": _('Orders'),
            "day_shipment_date_title": _('Today’s shipments'),
            "day_shipment_date": Order.objects.filter(shipment_date=today, organization=request.organization).count(),
            "day_shipment_date_url": f"{changelist_url}?{urlencode({'shipment_date': today, 'organization__id': request.organization.id})}",
            "week_shipment_date_title": _('Next 7 days’ shipments'),
            "week_shipment_date": Order.objects.filter(shipment_date__range=(today, next_week), organization=request.organization).count(),
            "week_shipment_date_url": f"{changelist_url}?{urlencode({'shipment_date__gte': today, 'shipment_date__lte': next_week, 'organization__id': request.organization.id})}",
            "day_delivery_date_title": _('Today’s deliveries'),
            "day_delivery_date": Order.objects.filter(delivery_date=today, organization=request.organization).count(),
            "day_delivery_date_url": f"{changelist_url}?{urlencode({'delivery_date': today, 'organization__id': request.organization.id})}",
            "week_delivery_date_title": _('Next 7 days’ deliveries'),
            "week_delivery_date": Order.objects.filter(delivery_date__range=(today, next_week), organization=request.organization).count(),
            "week_delivery_date_url": f"{changelist_url}?{urlencode({'delivery_date__gte': today, 'delivery_date__lte': next_week, 'organization__id': request.organization.id})}",
        }

    return TemplateResponse(request, "admin/index.html", context)

admin.site.index = custom_index.__get__(admin.site)
