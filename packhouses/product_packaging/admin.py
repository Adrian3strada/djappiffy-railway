from django.contrib import admin
from .models import PackerEmployee
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from .views import generate_label_pdf
from common.base.mixins import (ByOrganizationAdminMixin)

@admin.register(PackerEmployee)
class PackerEmployeeAdmin(ByOrganizationAdminMixin):
    list_display = ("full_name", "labels_number", "generate_label_button")  
    search_fields = ("full_name",)

    def has_add_permission(self, request):
        return False  

    def has_delete_permission(self, request, obj=None):
        return False  

    def has_change_permission(self, request, obj=None):
        return False

    def labels_number(self, obj):
        print(f"Generando formulario para el empleado con ID: {obj.id}") 
        html_output = format_html(
            '<form action="{}" method="get" id="form_{}">'
            '<input type="number" id="ticket_number_{}" name="quantity" value="10" min="1" style="width: 80px;">'
            '<input type="submit" style="display: none;">'
            '</form>',
            reverse("admin:generate_label", args=[obj.id]),
            obj.id,
            obj.id
        )
        print(html_output)
        return html_output
    labels_number.short_description = _("Quantity")

    def generate_label_button(self, obj):
        return format_html(
            '<button type="button" class="btn btn-primary" onclick="submitForm({})" '
            'style="padding: 1px 10px; text-decoration: none;">{}</button>',
            obj.id, 
            _("Generate labels")
        )

    generate_label_button.short_description = _("Actions")
    generate_label_button.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("generate_label/<int:employee_id>/", self.admin_site.admin_view(generate_label_pdf), name="generate_label"),
        ]
        return custom_urls + urls

    class Media:
        js = ('js/admin.js',)  

