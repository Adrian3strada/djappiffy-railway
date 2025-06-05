from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.translation import gettext as _
from .models import (Requisition, RequisitionSupply, Country, Region, SubRegion, City, PurchaseOrder, PurchaseOrderSupply,
                     PurchaseOrderCharge, PurchaseOrderDeduction, FruitPurchaseOrderReceipt)
from packhouses.catalogs.models import HarvestingCrew
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML, CSS
from io import BytesIO
from datetime import datetime
from django.db.models import Prefetch
from django.utils.text import capfirst
from django.db.models import Sum
from django.urls import reverse
from django.http import HttpResponseForbidden
from django.http import JsonResponse
from packhouses.storehouse.models import StorehouseEntrySupply
from django.views import View
from django.db import transaction
from django.utils import timezone
from .models import PurchaseMassPayment, PurchaseOrderPayment, ServiceOrderPayment
from .utils import get_name

def requisition_pdf(request, requisition_id):
    # Redirige al login del admin usando 'reverse' si el usuario no está autenticado.
    if not request.user.is_authenticated:
        login_url = reverse('admin:login')
        return redirect(login_url)

    # Obtener el registro
    requisition = get_object_or_404(
        Requisition,
        pk=requisition_id,
        organization=request.organization
    )

    # Obtener Datos de la Organización
    if hasattr(request, 'organization'):
        organization = request.organization.organizationprofile.name
        add =  request.organization.organizationprofile.address
        organization_profile = request.organization.organizationprofile

        # Obtener los nombres de las regiones
        city_name = get_name(SubRegion, organization_profile.city_id, "City")
        country_name = get_name(Country, organization_profile.country_id, "Country")
        state_name = get_name(Region, organization_profile.state_id, "State")
        district_name = get_name(City, organization_profile.district_id, "District")
        if organization_profile.logo:
            logo_url = organization_profile.logo.url
        else:
            logo_url = None
    pdf_title = f"{capfirst(Requisition._meta.verbose_name)}"
    packhouse_name = organization
    company_address = f"{add}, {district_name}, {city_name}, {state_name}, {country_name}"
    date = datetime.now()
    year = date.year

    # Obtener los inlines relacionados
    requisitionsupplyinline = RequisitionSupply.objects.filter(requisition=requisition)

    # CSS
    base_url = request.build_absolute_uri('/')
    css = CSS(string='''
        @page {
            size: letter portrait;
        }''')

    request_text = _("We hereby request the Purchasing Operations Department to acquire the necessary supplies as detailed in this document.")

    applicant_name = f"{requisition.user.first_name or ''} {requisition.user.last_name or ''}".strip()
    applicant_email = requisition.user.email or ""

    # Renderizar el template HTML
    html_string = render_to_string('admin/packhouses/sales-order-requisition-report.html', {
        'packhouse_name': packhouse_name,
        'company_address': company_address,
        'pdf_title': pdf_title,
        'logo_url': logo_url,
        'requisition': requisition,
        'requisitionsupplyinline': requisitionsupplyinline,
        'year': year,
        'date': date,
        'request_text': request_text,
        'applicant_name': applicant_name,
        'applicant_email': applicant_email,
    })

    # Convertir el HTML a PDF
    html = HTML(string=html_string, base_url=base_url)
    pdf_buffer = BytesIO()
    html.write_pdf(pdf_buffer, stylesheets=[css],)

    # Traducir el nombre del archivo manualmente
    filename = f"{_('requisition')}_{requisition.ooid}.pdf"

    # Devolver el PDF como respuesta
    pdf_buffer.seek(0)
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response


def set_requisition_ready(request, requisition_id):
    requisition = get_object_or_404(
        Requisition,
        pk=requisition_id,
        organization=request.organization
    )
    if requisition.status not in ['open']:
        return JsonResponse({
            'success': False,
            'message': 'You cannot send this requisition.'
        }, status=403)

    requisition.status = 'ready'
    requisition.save()
    success_message = _('Requisition sent to Purchase Operations Department successfully.')

    return JsonResponse({
        'success': True,
        'message': success_message
    })


def purchase_order_supply_pdf(request, purchase_order_supply_id):
    # Redirige al login del admin usando 'reverse' si el usuario no está autenticado.
    if not request.user.is_authenticated:
        login_url = reverse('admin:login')
        return redirect(login_url)

    # Obtener el registro
    purchase_order_supply = get_object_or_404(
        PurchaseOrder,
        pk=purchase_order_supply_id,
        organization=request.organization
    )
    # Obtener Datos de la Organización
    if hasattr(request, 'organization'):
        organization = request.organization.organizationprofile.name
        add = request.organization.organizationprofile.address
        organization_profile = request.organization.organizationprofile

        # Obtener los nombres de las regiones
        city_name = get_name(SubRegion, organization_profile.city_id, "City")
        country_name = get_name(Country, organization_profile.country_id, "Country")
        state_name = get_name(Region, organization_profile.state_id, "State")
        district_name = get_name(City, organization_profile.district_id, "District")
        if organization_profile.logo:
            logo_url = organization_profile.logo.url
        else:
            logo_url = None
    pdf_title = f"{capfirst(PurchaseOrder._meta.verbose_name)}"
    packhouse_name = organization
    company_address = f"{add}, {district_name}, {city_name}, {state_name}, {country_name}"
    date = datetime.now()
    year = date.year

    # Obtener los inlines relacionados
    purchaseordersupplyinline = PurchaseOrderSupply.objects.filter(purchase_order=purchase_order_supply)
    purchaseorderchargeinline = PurchaseOrderCharge.objects.filter(purchase_order=purchase_order_supply)
    purchaseorderdeductioninline = PurchaseOrderDeduction.objects.filter(purchase_order=purchase_order_supply)

    formatted_supply_values = []
    for obj in purchaseordersupplyinline:
        # Si el objeto está en inventario, buscar la cantidad recibida en StorehouseEntrySupply
        if obj.is_in_inventory:
            storehouse_entry_supply = StorehouseEntrySupply.objects.filter(
                purchase_order_supply=obj
            ).first()
            quantity = storehouse_entry_supply.received_quantity if storehouse_entry_supply else obj.quantity
        else:
            quantity = obj.quantity

        formatted_supply_values.append({
            'supply': f"{obj.requisition_supply.supply}",
            'quantity': quantity,
            'unit_price': obj.unit_price,
            'total_price': round(obj.unit_price * quantity,2),
        })

    formatted_charge_values = []
    for obj in purchaseorderchargeinline:
        formatted_charge_values.append({
            'charge': f"{obj.charge}",
            'amount': obj.amount,
        })

    formatted_deduction_values = []
    for obj in purchaseorderdeductioninline:
        formatted_deduction_values.append({
            'deduction': f"{obj.deduction}",
            'amount': obj.amount,
        })

    # Calcular el subtotal base
    subtotal = sum(item['total_price'] for item in formatted_supply_values)

    # Calcular el impuesto sobre el subtotal modificado
    percentage_tax = purchase_order_supply.tax
    tax = round(subtotal * (percentage_tax / 100), 2)

    # Calcular el total
    subtotal_with_tax = round(subtotal + tax, 2)

    # Sumar los cargos y restar las deducciones
    total = subtotal_with_tax + sum(item["amount"] for item in formatted_charge_values) - sum(
    item["amount"] for item in formatted_deduction_values)

    # Obtener la moneda
    currency = purchase_order_supply.currency.code

    # CSS
    base_url = request.build_absolute_uri('/')
    css = CSS(string='''
        @page {
            size: letter portrait;
        }''')


    applicant_name = f"{purchase_order_supply.user.first_name or ''} {purchase_order_supply.user.last_name or ''}".strip()
    applicant_email = purchase_order_supply.user.email or ""

    provider_text = _("Provider")
    payment_date_text = _("Payment date")
    order_date_text = _("Order date")

    # Renderizar el template HTML
    html_string = render_to_string('admin/packhouses/purchase-order-supply.html', {
        'packhouse_name': packhouse_name,
        'company_address': company_address,
        'pdf_title': pdf_title,
        'logo_url': logo_url,
        'purchase_order': purchase_order_supply,
        'purchaseorderupplyinline': purchaseordersupplyinline,
        'formatted_supply_values': formatted_supply_values,
        'year': year,
        'date': date,
        'applicant_name': applicant_name,
        'applicant_email': applicant_email,
        'subtotal': subtotal,
        'subtotal_with_tax': subtotal_with_tax,
        'percentage_tax': percentage_tax,
        'tax': tax,
        'total': total,
        'currency': currency,
        'provider_text': provider_text,
        'payment_date_text': payment_date_text,
        'order_date_text': order_date_text,
        'formatted_charge_values': formatted_charge_values,
        'formatted_deduction_values': formatted_deduction_values,
    })

    # Convertir el HTML a PDF
    html = HTML(string=html_string, base_url=base_url)
    pdf_buffer = BytesIO()
    html.write_pdf(pdf_buffer, stylesheets=[css], )

    # Traducir el nombre del archivo manualmente
    filename = f"{_('purchase_order')}_{purchase_order_supply.ooid}.pdf"

    # Devolver el PDF como respuesta
    pdf_buffer.seek(0)
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response

def set_purchase_order_supply_ready(request, purchase_order_supply_id):
    # Obtener el registro
    purchase_order_supply = get_object_or_404(
        PurchaseOrder,
        pk=purchase_order_supply_id,
        organization=request.organization
    )
    if purchase_order_supply.status not in ['open']:
        return JsonResponse({
            'success': False,
            'message': 'You cannot send this purchases order.'
        }, status=403)

    purchase_order_supply.status = 'ready'
    purchase_order_supply.save()
    success_message = _('Purchase order sent to Storehouse successfully.')

    return JsonResponse({
        'success': True,
        'message': success_message
    })

def set_purchase_order_supply_open(request, purchase_order_supply_id):
    # Obtener el registro
    purchase_order_supply = get_object_or_404(
        PurchaseOrder,
        pk=purchase_order_supply_id,
        organization=request.organization
    )
    if purchase_order_supply.status not in ['ready']:
        return JsonResponse({
            'success': False,
            'message': 'You cannot send this purchases order.',
            'title': 'Error'
        }, status=403)

    purchase_order_supply.status = 'open'
    purchase_order_supply.save()
    title_message = _('Success')
    success_message = _('Purchase order sent to Purchase successfully.')
    button_text = _('Continue')

    return JsonResponse({
        'success': True,
        'message': success_message,
        'title': title_message,
        'button': button_text
    })

def set_purchase_order_supply_payment(request, purchase_order_supply_id):
    # Obtener el registro
    purchase_order_supply = get_object_or_404(
        PurchaseOrder,
        pk=purchase_order_supply_id,
        organization=request.organization
    )
    if purchase_order_supply.status not in ['closed']:
        return JsonResponse({
            'success': False,
            'message': 'You cannot send this purchases order.',
            'title': 'Error'
        }, status=403)

    purchase_order_supply.is_in_payments = True
    purchase_order_supply.save()
    title_message = _('Success')
    success_message = _('Purchase order sent to Payments successfully.')
    button_text = _('Continue')

    return JsonResponse({
        'success': True,
        'message': success_message,
        'title': title_message,
        'button': button_text
    })

class CancelMassPaymentView(View):
    """
    Vista para cancelar un Mass Payment y sus pagos asociados de manera atómica.
    """
    def post(self, request, pk, *args, **kwargs):
        try:
            with transaction.atomic():
                # Bloqueo optimista
                mass_payment = PurchaseMassPayment.objects.select_for_update().get(pk=pk)

                if mass_payment.status == "canceled":
                    return JsonResponse({
                        "success": False,
                        "message": _("This Mass Payment is already canceled.")
                    }, status=400)

                # Cancelar todos los PurchaseOrderPayment asociados
                purchase_payments = PurchaseOrderPayment.objects.filter(mass_payment=mass_payment)
                for payment in purchase_payments:
                    payment.status = "canceled"
                    payment.cancellation_date = timezone.now()
                    payment.canceled_by = request.user
                    payment.save(update_fields=["status", "cancellation_date", "canceled_by"])

                    # Recalcular el balance de la orden de compra
                    payment.purchase_order.recalculate_balance(save=True)

                # Cancelar todos los ServiceOrderPayment asociados
                service_payments = ServiceOrderPayment.objects.filter(mass_payment=mass_payment)
                for payment in service_payments:
                    payment.status = "canceled"
                    payment.cancellation_date = timezone.now()
                    payment.canceled_by = request.user
                    payment.save(update_fields=["status", "cancellation_date", "canceled_by"])

                    # Recalcular el balance de la orden de servicio
                    payment.service_order.recalculate_balance(save=True)

                # Actualizamos el estado del Mass Payment a cancelado
                mass_payment.status = "canceled"
                mass_payment.cancellation_date = timezone.now()
                mass_payment.canceled_by = request.user
                mass_payment.save(update_fields=["status", "cancellation_date", "canceled_by"])

            # Retornar un JSON de éxito
            return JsonResponse({
                "success": True,
                "message": _("Mass Payment and its related payments were canceled successfully.")
            })

        except PurchaseMassPayment.DoesNotExist:
            return JsonResponse({
                "success": False,
                "message": _("Mass Payment not found")
            }, status=404)
        except Exception as e:
            return JsonResponse({
                "success": False,
                "message": f"Error: {str(e)}"
            }, status=500)

def get_receipts_for_order(request):
    order_id = request.GET.get('order_id')
    if not order_id:
        return JsonResponse([], safe=False)

    receipts = FruitPurchaseOrderReceipt.objects.filter(
        fruit_purchase_order_id=order_id
    ).values('id', 'ooid')

    return JsonResponse(list(receipts), safe=False)
