from django.contrib import admin
from .models import PackerEmployee, PackerLabel
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from .views import generate_label_pdf, generate_pending_label_pdf
from common.base.mixins import (ByOrganizationAdminMixin)

@admin.register(PackerEmployee)
class PackerEmployeeAdmin(ByOrganizationAdminMixin):
    list_display = ("full_name", "labels_number_and_generate_button", "pending_labels")  
    search_fields = ("full_name",)

    def has_add_permission(self, request):
        return False  

    def has_delete_permission(self, request, obj=None):
        return False  

    def has_change_permission(self, request, obj=None):
        return False
    
    def labels_number_and_generate_button(self, obj):
        return format_html(
            '<form action="{}" method="get" id="form_{}" style="display:inline-block;">'
                '<input type="number" id="ticket_number_{}" name="quantity" value="10" min="1" max="1000" '
                'style="width: 80px;" onkeydown="if(event.keyCode !== 38 && event.keyCode !== 40) return false;">'
                '<button type="button" class="btn btn-primary" onclick="submitForm({})" '
                'style="padding: 1px 10px; text-decoration: none; margin-left:5px;">{}'
                '</button>'
                '<input type="submit" style="display:none;">'
            '</form>',
            reverse("admin:generate_label", args=[obj.id]),
            obj.id,
            obj.id,
            obj.id,
            _("Generate labels")
        )
    labels_number_and_generate_button.short_description = _("Actions")
    labels_number_and_generate_button.allow_tags = True

#  ***************************************** WORKING
    def pending_labels(self, obj):
        pending_count = PackerLabel.objects.filter(employee=obj, scanned_at__isnull=True).count()

        return format_html(
            '<div style="display: flex; align-items: center; gap: 10px;">'
            '    <input type="text" id="pending_quantity_{}" value="{}" readonly '
            '           style="width: 80px; text-align: center; background-color: #f8f9fa; border: 1px solid #ced4da;">'
            '    <button type="button" class="btn btn-primary" onclick="submitFormPending({})">{}</button>'
            '    <button type="button" class="btn btn-danger" onclick="discardLabels({})">{}</button>'
            '</div>'
            '<script>'
            'function discardLabels(employeeId) {{'
            '    if (confirm("Are you sure you want to discard all pending labels?")) {{'
            '        fetch("/admin/discard_labels/" + employeeId + "/", {{ method: "POST", headers: {{ "X-CSRFToken": getCSRFToken() }} }})'
            '        .then(response => response.json())'
            '        .then(data => {{'
            '            if (data.status === "success") {{'
            '                alert("Deleted " + data.deleted + " labels.");'
            '                location.reload();'
            '            }} else {{'
            '                alert("Error: " + data.message);'
            '            }}'
            '        }});'
            '    }}'
            '}}'
            'function getCSRFToken() {{'
            '    return document.querySelector("[name=csrfmiddlewaretoken]").value;'
            '}}'
            '</script>',
            obj.id,
            pending_count,
            obj.id, 
            _("Reprint"),
            reverse("admin:generate_pending_labels", args=[obj.id]), 
            _("Discard"), 
            _("No hace nada")                  #REVISAR 
        )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("generate_label/<int:employee_id>/", self.admin_site.admin_view(generate_label_pdf), name="generate_label"),
            path("generate_pending_labels/<int:employee_id>/", self.admin_site.admin_view(generate_pending_label_pdf), name="generate_pending_labels"),
        ]
        return custom_urls + urls

    class Media:
        js = ('js/admin.js',)  

