from django.urls import reverse
from django.utils.http import urlencode
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
from packhouses.receiving.models import Batch, IncomingProduct, FoodSafety
from packhouses.gathering.models import ScheduleHarvest
from packhouses.sales.models import Order
from packhouses.certifications.models import CertificationDocument, Certification
from packhouses.purchases.models import Requisition, PurchaseOrder, ServiceOrder, PurchaseOrder
from packhouses.storehouse.models import AdjustmentInventory, StorehouseEntry

def get_common_periods():
    today = timezone.now().date()
    return {
        "today": today,
        "week_ago": today - timedelta(days=7),
        "two_week_ago": today - timedelta(days=15),
        "month_ago": today - timedelta(days=30),
        "next_week": today + timedelta(days=7),
        "next_two_week": today + timedelta(days=15),
        "next_month": today + timedelta(days=30),
        "next_two_month": today + timedelta(days=60),
        "next_three_month": today + timedelta(days=90),
        "day_title": _("Today"),
        "week_ago_title": _("Last 7 days"),
        "two_week_ago_title": _("Last 15 days"),
        "month_ago_title": _("Last 30 days"),
        "next_week_title": _("Next 7 days"),
        "next_two_week_title": _("Next 15 days"),
        "next_month_title": _("Next 30 days"),
        "next_two_month_title": _("Next 60 days"),
        "next_three_month_title": _("Next 90 days"),
    }

def get_order_block(title, status, organization, changelist_url):
    filters = {"status": status, "organization": organization}

    def get_item(label, filter_key, filter_value_end, filter_value_start=None):
        f = filters.copy()
        f_url = filters.copy()

        if filter_key.endswith("__range") and filter_value_start is not None:
            f[filter_key] = (filter_value_start, filter_value_end)

            base_field = filter_key.replace("__range", "")
            f_url[f"{base_field}__gte"] = filter_value_start
            f_url[f"{base_field}__lte"] = filter_value_end

        else:
            f[filter_key] = filter_value_end
            f_url[filter_key] = filter_value_end

        return {
            "title": _(label),
            "count": Order.objects.filter(**f).count(),
            "url": f"{changelist_url}?{urlencode({**f_url})}"
        }

    periods = get_common_periods()

    if status == 'ready':
        items = [
            get_item("Today’s shipments", "shipment_date", periods["today"], None),
            get_item("Next 15 days’ shipments", "shipment_date__range", periods["next_two_week"], periods["today"]),
            get_item("Today’s deliveries", "delivery_date", periods["today"], None),
            get_item("Next 15 days’ deliveries", "delivery_date__range", periods["next_two_week"], periods["today"]),
        ]
    else:
        items = [
            get_item(periods["day_title"], "created_at__date", periods["today"], None),
            get_item(periods["week_ago_title"], "created_at__date__gte", periods["week_ago"], None),
            get_item(periods["two_week_ago_title"], "created_at__date__gte", periods["two_week_ago"], None),
        ]

    return {
        "block_name": _(title),
        "items": items
    }

def get_scheduleharvest_block(title, status, organization, changelist_url):
    filters = {"status": status, "organization": organization}

    def get_item(label, filter_key, filter_value_end, filter_value_start=None):
        f = filters.copy()
        f_url = filters.copy()

        if filter_key.endswith("__range") and filter_value_start is not None:
            f[filter_key] = (filter_value_start, filter_value_end)

            base_field = filter_key.replace("__range", "")
            f_url[f"{base_field}__gte"] = filter_value_start
            f_url[f"{base_field}__lte"] = filter_value_end

        else:
            f[filter_key] = filter_value_end
            f_url[filter_key] = filter_value_end

        return {
            "title": _(label),
            "count": ScheduleHarvest.objects.filter(**f).count(),
            "url": f"{changelist_url}?{urlencode({**f_url})}"
        }

    periods = get_common_periods()

    if status == 'ready':
        items = [
            get_item(periods["day_title"], "harvest_date", periods["today"], None),
            get_item(periods["next_week_title"], "harvest_date__range", periods["next_week"], periods["today"]),
            get_item(periods["next_two_week_title"], "harvest_date__range", periods["next_two_week"], periods["today"]),
        ]
    else:
        items = [
            get_item(periods["day_title"], "created_at__date", periods["today"], None),
            get_item(periods["week_ago_title"], "created_at__date__gte", periods["week_ago"], None),
            get_item(periods["two_week_ago_title"], "created_at__date__gte", periods["two_week_ago"], None),
        ]

    return {
        "block_name": _(title),
        "items": items
    }

def get_incomingproduct_block(title, status, is_quarantined, organization, changelist_url):
    filters = {"status": status, "organization": organization}

    if is_quarantined is not None:
        filters["is_quarantined"] = int(is_quarantined)

    def get_item(label, filter_key, filter_value):
        f = filters.copy()
        f[filter_key] = filter_value

        return {
            "title": _(label),
            "count": IncomingProduct.objects.filter(**f).count(),
            "url": f"{changelist_url}?{urlencode({**f})}"
        }

    periods = get_common_periods()

    items = [
        get_item(periods["day_title"], "created_at__date", periods["today"]),
        get_item(periods["week_ago_title"], "created_at__date__gte", periods["week_ago"]),
        get_item(periods["two_week_ago_title"], "created_at__date__gte", periods["two_week_ago"]),
    ]

    return {
        "block_name": _(title),
        "items": items
    }

def get_batch_block(title, status, is_available_for_processing, organization, changelist_url):
    filters = {"status": status, "organization": organization}
    if is_available_for_processing is not None:
        filters["is_available_for_processing"] = int(is_available_for_processing)

    def get_item(label, filter_key, filter_value):
        f = filters.copy()
        f[filter_key] = filter_value

        return {
            "title": _(label),
            "count": Batch.objects.filter(**f).count(),
            "url": f"{changelist_url}?{urlencode({**f})}"
        }

    periods = get_common_periods()

    items = [
        get_item(periods["day_title"], "created_at__date", periods["today"]),
        get_item(periods["week_ago_title"], "created_at__date__gte", periods["week_ago"]),
        get_item(periods["two_week_ago_title"], "created_at__date__gte", periods["two_week_ago"]),
    ]

    return {
        "block_name": _(title),
        "items": items
    }

def get_foodsafety_block(title, status, organization, changelist_url):
    filters = {"status": status, "organization": organization}

    def get_item(label, filter_key, filter_value):
        f = filters.copy()
        f[filter_key] = filter_value

        return {
            "title": _(label),
            "count": FoodSafety.objects.filter(**f).count(),
            "url": f"{changelist_url}?{urlencode({**f})}"
        }

    periods = get_common_periods()

    items = [
        get_item(periods["day_title"], "created_at__date", periods["today"]),
        get_item(periods["week_ago_title"], "created_at__date__gte", periods["week_ago"]),
        get_item(periods["two_week_ago_title"], "created_at__date__gte", periods["two_week_ago"]),
    ]

    return {
        "block_name": _(title),
        "items": items
    }

def get_certification_block(title, organization, changelist_url):
    filters = {"certification__organization": organization}

    def get_item(label, filter_key, filter_value_end, filter_value_start):
        f = filters.copy()
        f[filter_key] = (filter_value_start, filter_value_end)
        certification_ids = CertificationDocument.objects.filter(**f).values_list('certification', flat=True).distinct()

        return {
            "title": _(label),
            "count": certification_ids.count(),
            "url": f"{changelist_url}?{urlencode({'id__in': ','.join(str(id) for id in certification_ids)})}"
        }

    periods = get_common_periods()

    items = [
        get_item(periods["next_month_title"], "expiration_date__range", periods["next_month"], periods["today"]),
        get_item(periods["next_two_month_title"], "expiration_date__range", periods["next_two_month"], periods["today"]),
        get_item(periods["next_three_month_title"], "expiration_date__range", periods["next_three_month"], periods["today"]),
    ]

    return {
        "block_name": _(title),
        "items": items
    }

def get_requisition_block(title, status, past, parment_date, organization, changelist_url):
    filters = {"status": status, "organization": organization}

    def get_item(label, filter_key, filter_value_end, filter_value_start=None):
        f = filters.copy()
        f_url = filters.copy()

        if filter_key.endswith("__range") and filter_value_start is not None:
            f[filter_key] = (filter_value_start, filter_value_end)

            base_field = filter_key.replace("__range", "")
            f_url[f"{base_field}__gte"] = filter_value_start
            f_url[f"{base_field}__lte"] = filter_value_end

        else:
            f[filter_key] = filter_value_end
            f_url[filter_key] = filter_value_end

        return {
            "title": _(label),
            "count": Requisition.objects.filter(**f).count(),
            "url": f"{changelist_url}?{urlencode({**f})}"
        }

    periods = get_common_periods()

    if past:
        if parment_date:
            items = [
                get_item(periods["day_title"], "payment_date", periods["today"], None),
                get_item(periods["two_week_ago_title"], "payment_date__gte", periods["two_week_ago"], None),
                get_item(periods["month_ago_title"], "payment_date__gte", periods["month_ago"], None),
            ]
        else:
            items = [
                get_item(periods["day_title"], "created_at__date", periods["today"], None),
                get_item(periods["two_week_ago_title"], "created_at__date__gte", periods["two_week_ago"], None),
                get_item(periods["month_ago_title"], "created_at__date__gte", periods["month_ago"], None),
            ]
    else:
        items = [
            get_item(periods["day_title"], "payment_date", periods["today"], None),
            get_item(periods["next_two_week_title"], "payment_date__range", periods["next_two_week"], periods["today"]),
            get_item(periods["next_month_title"], "payment_date__range", periods["next_month"], periods["today"]),
        ]

    return {
        "block_name": _(title),
        "items": items
    }

def get_service_block(title, status, filter_field, past, parment_date, organization, changelist_url):
    filters = {"status": status, "organization": organization}

    if filter_field is not None and filter_field=="":
        filters[f"{filter_field}__isnull"] = False

    def get_item(label, filter_key, filter_value_end, filter_value_start=None):
        f = filters.copy()
        f_url = filters.copy()

        if filter_key.endswith("__range") and filter_value_start is not None:
            f[filter_key] = (filter_value_start, filter_value_end)

            base_field = filter_key.replace("__range", "")
            f_url[f"{base_field}__gte"] = filter_value_start
            f_url[f"{base_field}__lte"] = filter_value_end

        else:
            f[filter_key] = filter_value_end
            f_url[filter_key] = filter_value_end

        return {
            "title": _(label),
            "count": ServiceOrder.objects.filter(**f).count(),
            "url": f"{changelist_url}?{urlencode({**f_url})}"
        }

    periods = get_common_periods()

    if past:
        if parment_date:
            items = [
                get_item(periods["day_title"], "payment_date", periods["today"], None),
                get_item(periods["two_week_ago_title"], "payment_date__gte", periods["two_week_ago"], None),
                get_item(periods["month_ago_title"], "payment_date__gte", periods["month_ago"], None),
            ]
        else:
            items = [
                get_item(periods["day_title"], "created_at__date", periods["today"], None),
                get_item(periods["two_week_ago_title"], "created_at__date__gte", periods["two_week_ago"], None),
                get_item(periods["month_ago_title"], "created_at__date__gte", periods["month_ago"], None),
            ]
    else:
        items = [
            get_item(periods["day_title"], "payment_date", periods["today"], None),
            get_item(periods["next_two_week_title"], "payment_date__range", periods["next_two_week"], periods["today"]),
            get_item(periods["next_month_title"], "payment_date__range", periods["next_month"], periods["today"]),
        ]

    return {
        "block_name": _(title),
        "items": items
    }

def get_purchase_block(title, status, past, parment_date, organization, changelist_url):
    filters = {"status": status, "organization": organization}

    def get_item(label, filter_key, filter_value_end, filter_value_start=None):
        f = filters.copy()
        f_url = filters.copy()

        if filter_key.endswith("__range") and filter_value_start is not None:
            f[filter_key] = (filter_value_start, filter_value_end)

            base_field = filter_key.replace("__range", "")
            f_url[f"{base_field}__gte"] = filter_value_start
            f_url[f"{base_field}__lte"] = filter_value_end

        else:
            f[filter_key] = filter_value_end
            f_url[filter_key] = filter_value_end

        return {
            "title": _(label),
            "count": PurchaseOrder.objects.filter(**f).count(),
            "url": f"{changelist_url}?{urlencode({**f})}"
        }

    periods = get_common_periods()

    if past:
        if parment_date:
            items = [
                get_item(periods["day_title"], "payment_date", periods["today"], None),
                get_item(periods["two_week_ago_title"], "payment_date__gte", periods["two_week_ago"], None),
                get_item(periods["month_ago_title"], "payment_date__gte", periods["month_ago"], None),
            ]
        else:
            items = [
                get_item(periods["day_title"], "created_at__date", periods["today"], None),
                get_item(periods["two_week_ago_title"], "created_at__date__gte", periods["two_week_ago"], None),
                get_item(periods["month_ago_title"], "created_at__date__gte", periods["month_ago"], None),
            ]
    else:
        items = [
            get_item(periods["day_title"], "payment_date", periods["today"], None),
            get_item(periods["next_two_week_title"], "payment_date__range", periods["next_two_week"], periods["today"]),
            get_item(periods["next_month_title"], "payment_date__range", periods["next_month"], periods["today"]),
        ]

    return {
        "block_name": _(title),
        "items": items
    }

def get_adjustment_block(title, bound, organization, changelist_url):
    filters = {"transaction_kind": bound , "organization": organization}

    def get_item(label, filter_key, filter_value):
        f = filters.copy()
        f[filter_key] = filter_value

        return {
            "title": _(label),
            "count": AdjustmentInventory.objects.filter(**f).count(),
            "url": f"{changelist_url}?{urlencode({**f})}"
        }

    periods = get_common_periods()

    items = [
        get_item(periods["day_title"], "created_at__date", periods["today"]),
        get_item(periods["two_week_ago_title"], "created_at__date__gte", periods["two_week_ago"]),
        get_item(periods["month_ago_title"], "created_at__date__gte", periods["month_ago"]),
    ]

    return {
        "block_name": _(title),
        "items": items
    }

def get_storehouse_block(title, organization, changelist_url):
    filters = {"organization": organization}

    def get_item(label, filter_key, filter_value):
        f = filters.copy()
        f[filter_key] = filter_value

        return {
            "title": _(label),
            "count": StorehouseEntry.objects.filter(**f).count(),
            "url": f"{changelist_url}?{urlencode({**f})}"
        }

    periods = get_common_periods()

    items = [
        get_item(periods["day_title"], "created_at__date", periods["today"]),
        get_item(periods["two_week_ago_title"], "created_at__date__gte", periods["two_week_ago"]),
        get_item(periods["month_ago_title"], "created_at__date__gte", periods["month_ago"]),
    ]

    return {
        "block_name": _(title),
        "items": items
    }