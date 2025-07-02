from nested_admin import NestedInlineModelAdminMixin
from django.utils.translation import gettext_lazy as _
from django.utils.formats import date_format
from django.utils.html import format_html
from django.contrib.admin.templatetags.admin_list import _boolean_icon

class CustomNestedStackedInlineMixin(NestedInlineModelAdminMixin):
    template = "nested_stacked.html"

class CustomNestedStackedAvgInlineMixin(NestedInlineModelAdminMixin):
    template = "nested_stacked_avg.html"

class IncomingProductMetricsMixin:
    readonly_fields = (
        'display_weighed_sets_count',
        'display_containers_count',
        'display_total_net_weight',
        'display_average_weight_per_container',
        'display_assigned_containers',
        'display_full_containers_per_harvest',
        'display_empty_containers',
        'display_missing_containers',
    )

    def display_weighed_sets_count(self, obj):
        return obj.weighed_sets_count
    display_weighed_sets_count.short_description = _("Total Weighed Sets")

    def display_containers_count(self, obj):
        return obj.containers_count
    display_containers_count.short_description = _("Total Containers")

    def display_total_net_weight(self, obj):
        return obj.total_net_weight
    display_total_net_weight.short_description = _("Total Net Weight")

    def display_average_weight_per_container(self, obj):
        return obj.average_weight_per_container
    display_average_weight_per_container.short_description = _("Average Weight per Container")

    def display_assigned_containers(self, obj):
        return obj.assigned_container_total
    display_assigned_containers.short_description = _("Assigned Containers")

    def display_full_containers_per_harvest(self, obj):
        return obj.full_container_total
    display_full_containers_per_harvest.short_description = _("Full Containers per Harvest")

    def display_empty_containers(self, obj):
        return obj.empty_container_total
    display_empty_containers.short_description = _("Empty Containers")

    def display_missing_containers(self, obj):
        return obj.missing_container_total
    display_missing_containers.short_description = _("Missing Containers")


class BatchDisplayMixin:
    def display_weight_received(self, obj):
        return '{:,.3f} kg'.format(obj.family_ingress_weight)
    display_weight_received.short_description = _('Ingress Weight (with children)')

    def display_available_weight(self, obj):
        return '{:,.3f} kg'.format(obj.available_weight)
    display_available_weight.short_description = _('Available Weight (with children)')

    def display_own_weight_received(self, obj):
        return '{:,.3f} kg'.format(obj.self_weighing_weight)
    display_own_weight_received.short_description = _('Self Ingress Weight')

    def display_own_net_received(self, obj):
        return '{:,.3f} kg'.format(obj.self_available_weight)
    display_own_net_received.short_description = _('Self Available Weight')

    def weight_received_display(self, obj):
        return f"{obj.family_ingress_weight:.3f}" if obj.family_ingress_weight else ""
    weight_received_display.short_description = _('Weight Received')

    def get_batch_available_weight(self, obj):
        total = obj.available_weight
        return '{:,.3f}'.format(total) if total else ''
    get_batch_available_weight.short_description = _('Available Weight')

    def display_batch_role(self, obj):
        if obj.is_parent:
            return _('Parent of batches: %s') % obj.children_list
        elif obj.is_child:
            return _('Child of batch: %s.') % obj.parent_batch_ooid
        return _(' ')
    display_batch_role.short_description = _('Batch Relationship')

    def get_batch_merge_status(self, obj):
        if obj.is_parent:
            children_ids = [str(child.ooid) for child in obj.children.all()]
            children_text = f" [{', '.join(children_ids)}]" if children_ids else ""
            return f"Parent{children_text}"
        elif obj.is_child:
            return f"Child of {obj.parent.ooid}"
        return _("Independent")

    get_batch_merge_status.short_description = _('Batch Merge Status')
    get_batch_merge_status.admin_order_field = 'parent'

    def get_scheduleharvest_ooid(self, obj):
        incoming = getattr(obj, 'incomingproduct', None)
        scheduleharvest = getattr(incoming, 'scheduleharvest', None) if incoming else None
        return str(scheduleharvest.ooid) if scheduleharvest and scheduleharvest.ooid is not None else "-"
    get_scheduleharvest_ooid.short_description = _('Harvest')
    get_scheduleharvest_ooid.admin_order_field = 'incomingproduct__scheduleharvest__ooid'

    def get_scheduleharvest_harvest_date(self, obj):
        incoming_product = getattr(obj, 'incomingproduct', None)
        schedule_harvest = getattr(incoming_product, 'scheduleharvest', None) if incoming_product else None

        if schedule_harvest and schedule_harvest.harvest_date:
            date_str = date_format(schedule_harvest.harvest_date, format='DATE_FORMAT', use_l10n=True)
        else:
            date_str = ''

        return format_html(
            '<span style="display:inline-block; min-width:80px;">{}</span>',
            date_str
        )
    get_scheduleharvest_harvest_date.short_description = _("Schedule Harvest Date")
    get_scheduleharvest_harvest_date.admin_order_field = 'incomingproduct__scheduleharvest__harvest_date'

    def get_scheduleharvest_product(self, obj):
        incoming_product = getattr(obj, 'incomingproduct', None)
        schedule_harvest = getattr(incoming_product, 'scheduleharvest', None) if incoming_product else None

        if schedule_harvest and schedule_harvest.product:
            return str(schedule_harvest.product)
        return ''
    get_scheduleharvest_product.short_description = _('Product')
    get_scheduleharvest_product.admin_order_field = 'incomingproduct__scheduleharvest__product'

    def get_scheduleharvest_product_provider(self, obj):
        incoming_product = getattr(obj, 'incomingproduct', None)
        schedule_harvest = getattr(incoming_product, 'scheduleharvest', None) if incoming_product else None
        product_provider = getattr(schedule_harvest, 'product_provider', None) if schedule_harvest else None

        return str(product_provider) if product_provider else ''
    get_scheduleharvest_product_provider.short_description = _('Product Provider')
    get_scheduleharvest_product_provider.admin_order_field = 'incomingproduct__scheduleharvest__product_provider'

    def get_scheduleharvest_product_variety(self, obj):
        incoming_product = getattr(obj, 'incomingproduct', None)
        schedule_harvest = getattr(incoming_product, 'scheduleharvest', None) if incoming_product else None
        product_variety = getattr(schedule_harvest, 'product_variety', None) if schedule_harvest else None

        return str(product_variety) if product_variety else ''
    get_scheduleharvest_product_variety.short_description = _('Product Variety')
    get_scheduleharvest_product_variety.admin_order_field = 'incomingproduct__scheduleharvest__product'

    def get_scheduleharvest_product_phenology(self, obj):
        incoming_product = getattr(obj, 'incomingproduct', None)
        schedule_harvest = getattr(incoming_product, 'scheduleharvest', None) if incoming_product else None
        product_phenology = getattr(schedule_harvest, 'product_phenology', None) if schedule_harvest else None

        return str(product_phenology) if product_phenology else ''
    get_scheduleharvest_product_phenology.short_description = _('Product Phenology')
    get_scheduleharvest_product_phenology.admin_order_field = 'incomingproduct__scheduleharvest__product'

    def get_scheduleharvest_orchards(self, obj):
        incoming_product = getattr(obj, 'incomingproduct', None)
        schedule_harvest = getattr(incoming_product, 'scheduleharvest', None) if incoming_product else None
        orchard = getattr(schedule_harvest, 'orchard', None) if schedule_harvest else None

        return str(orchard.name) if orchard else ''
    get_scheduleharvest_orchards.short_description = _('Orchard')
    get_scheduleharvest_orchards.admin_order_field = 'incomingproduct__scheduleharvest__orchard'

    def display_available_for_processing(self, obj):
        if obj.is_child:
            return ''
        return _boolean_icon(obj.is_available_for_processing)
    display_available_for_processing.short_description = _('Available for Processing')
    display_available_for_processing.admin_order_field = 'is_available_for_processing'

    def get_orchard_code(self, obj):
        return obj.incomingproduct.scheduleharvest.orchard.code if obj.incomingproduct.scheduleharvest.orchard else None
    get_orchard_code.short_description = _('Orchard Code')
    get_orchard_code.admin_order_field = 'incomingproduct__scheduleharvest__orchard__code'

    def get_orchard_product_producer(self, obj):
        schedule_harvest = obj.incomingproduct.scheduleharvest
        return schedule_harvest.orchard.producer if schedule_harvest else None
    get_orchard_product_producer.admin_order_field = 'incomingproduct__scheduleharvest__orchard__producer'
    get_orchard_product_producer.short_description = _('Product Producer')

    def get_orchard_category(self, obj):
        if obj.incomingproduct.scheduleharvest.orchard:
            return obj.incomingproduct.scheduleharvest.orchard.get_category_display()
        return None
    get_orchard_category.short_description = _('Product Category')
    get_orchard_category.admin_order_field = 'incomingproduct__scheduleharvest__orchard__category'

    def get_product_ripeness(self, obj):
        return obj.incomingproduct.scheduleharvest.product_ripeness if obj.incomingproduct.scheduleharvest else None
    get_product_ripeness.short_description = _('Product Ripeness')
    get_product_ripeness.admin_order_field = 'incomingproduct__scheduleharvest__product_ripeness'
