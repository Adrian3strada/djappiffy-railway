from nested_admin import NestedInlineModelAdminMixin
from django.utils.translation import gettext_lazy as _

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
    display_average_weight_per_container.short_description = _("Avg. Weight per Container")

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
