from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from packhouses.purchases.models import PurchaseOrderSupply


class PurchaseOrderSupplySerializer(serializers.ModelSerializer):
    purchase_order_supply_options = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrderSupply
        fields = ("id", "requisition_supply", "quantity", 'unit_category', 'delivery_deadline',
                  "comments", "is_in_inventory", "purchase_order_supply_options")

    def get_purchase_order_supply_options(self, obj):
        unit_mapping = {
            "cm": _("meters"),
            "ml": _("liters"),
            "gr": _("kilograms"),
            "piece": _("pieces"),
        }

        return [
            {
                "id": pos.id,
                "kind": str(pos.requisition_supply.supply.kind.usage_discount_unit_category),
                "name": str(pos.requisition_supply.supply),
                "unit": unit_mapping.get(
                    getattr(pos.requisition_supply.supply.kind.usage_discount_unit_category, "unit_category", ""),
                    getattr(pos.requisition_supply.supply.kind.usage_discount_unit_category, "unit_category", "")
                ),
                "real_unit": str(pos.requisition_supply.supply.kind.usage_discount_unit_category.unit_category),
            }
            for pos in PurchaseOrderSupply.objects.filter(purchase_order=obj.purchase_order)
        ]
