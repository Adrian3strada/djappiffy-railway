from django.contrib import admin

class OrganizationSupplyFilter(admin.SimpleListFilter):
    title = 'Supply'
    parameter_name = 'supply'

    def lookups(self, request, model_admin):
        """
        Define las opciones que aparecerán en el filtro.
        Solo incluirá supplies de la organización actual.
        """
        if hasattr(request, 'organization'):
            supplies = model_admin.model.objects.filter(
                organization=request.organization
            ).select_related('supply__kind').values_list(
                'supply__id',
                'supply__name',
                'supply__kind__name'
            ).distinct()
            return [(supply_id, f"{kind_name}: {name}") for supply_id, name, kind_name in supplies]
        return []

    def queryset(self, request, queryset):
        """
        Aplica el filtro seleccionado en la lista.
        """
        if self.value():
            return queryset.filter(supply__id=self.value())
        return queryset
