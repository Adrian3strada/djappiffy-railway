from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from packhouses.purchases.models import PurchaseOrderSupply


class PurchaseOrderSupplySerializer(serializers.ModelSerializer):
    purchase_order_supply_options = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrderSupply
        fields = (
            "id",
            "requisition_supply",
            "quantity",
            "unit_category",
            "delivery_deadline",
            "comments",
            "is_in_inventory",
            "purchase_order_supply_options",
        )

    def get_purchase_order_supply_options(self, obj):
        supplies = PurchaseOrderSupply.objects.filter(purchase_order=obj.purchase_order)
        results = []

        for pos in supplies:
            kind = pos.requisition_supply.supply.kind
            unit_category_obj = getattr(kind, "usage_discount_unit_category", None)

            translated_unit = str(unit_category_obj) if unit_category_obj else ""

            results.append({
                "id": pos.id,
                "kind": str(kind),
                "name": str(pos.requisition_supply.supply),
                "unit": translated_unit,  # Mostramos el nombre traducido de la categoría
                "real_unit": translated_unit,  # O lo que necesites aquí
            })

        return results

