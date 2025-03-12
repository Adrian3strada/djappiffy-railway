from nested_admin import NestedInlineModelAdminMixin

class CustomNestedStackedInlineMixin(NestedInlineModelAdminMixin):
    template = "nested_stacked.html" 