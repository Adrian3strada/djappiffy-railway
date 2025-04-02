from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from weasyprint import HTML
from django.template.loader import render_to_string
from .models import PackerEmployee, PackerLabel
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from ..hrm.models import Employee
import qrcode
from io import BytesIO
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import uuid
import base64

# Create your views here.

def generate_label_pdf(request, employee_id):
    employee = get_object_or_404(PackerEmployee, id=employee_id)

    quantity = request.GET.get("quantity", 10)
    quantity = int(quantity) if str(quantity).isdigit() else 10

    current_datetime = now().strftime("%Y-%m-%d %H:%M:%S")

    labels = []
    for _ in range(quantity):
        label_uuid = uuid.uuid4()
        
        label = PackerLabel.objects.create(
            employee=employee,
            uuid=label_uuid,
        )
        
        qr_data = f"{employee.id}-{label_uuid}"
        qr_image = qrcode.make(label.uuid)

        qr_io = BytesIO()
        qr_image.save(qr_io, format="PNG")
        qr_base64 = base64.b64encode(qr_io.getvalue()).decode("utf-8")

        labels.append({
            "label_id": qr_data,
            "qr_image_base64": qr_base64
        })

    html_string = render_to_string(
        "label_pdf.html",
        {
            "employee": employee,
            "labels": labels,
            "current_datetime": current_datetime
        }
    )

    pdf = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="labels_{employee.full_name}.pdf"'
    return response

def generate_pending_label_pdf(request, employee_id):
    employee = get_object_or_404(PackerEmployee, id=employee_id)

    pending_labels = PackerLabel.objects.filter(employee=employee, scanned_at__isnull=True)

    if not pending_labels.exists():
        return HttpResponse("No pending labels found", status=404)

    current_datetime = now().strftime("%Y-%m-%d %H:%M:%S")

    labels = []

    for label in pending_labels:
        qr_data = f"{employee.id}-{label.uuid}"
        qr_image = qrcode.make(label.uuid)

        qr_io = BytesIO()
        qr_image.save(qr_io, format="PNG")
        qr_base64 = base64.b64encode(qr_io.getvalue()).decode("utf-8")

        labels.append({
            "label_id": qr_data,
            "qr_image_base64": qr_base64
        })

    html_string = render_to_string(
        "label_pdf.html",
        {
            "employee": employee,
            "labels": labels,
            "current_datetime": current_datetime
        }
    )

    pdf = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="labels_{employee.full_name}_pending.pdf"'
    return response


@csrf_exempt  # Si usas AJAX sin CSRF token, puedes quitarlo si lo manejas correctamente
def discard_labels(request, employee_id):
    if request.method == "POST":
        employee = get_object_or_404(Employee, id=employee_id)
        deleted_count, _ = PackerLabel.objects.filter(employee=employee, scanned_at__isnull=True).delete()
        return JsonResponse({"status": "success", "deleted": deleted_count})

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)
