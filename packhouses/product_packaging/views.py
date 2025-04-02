from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from weasyprint import HTML
from django.template.loader import render_to_string
from .models import PackerEmployee
from django.utils.timezone import now

# Create your views here.
def generate_label_pdf(request, employee_id):
    employee = get_object_or_404(PackerEmployee, id=employee_id)
    quantity = request.GET.get("quantity", 10)  # Valor por defecto de 10
    if not quantity.isdigit():
        quantity = 10
    else:
        quantity = int(quantity)

    current_datetime = now().strftime("%Y-%m-%d %H:%M:%S")

    # Pasar un rango en lugar de un número
    html_string = render_to_string(
        "label_pdf.html", 
        {
            "employee": employee, 
            "quantity_range": range(quantity), 
            "current_datetime": current_datetime,
        }
    )

    pdf = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="labels_{employee.full_name}.pdf"'
    return response
