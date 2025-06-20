from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from packhouses.gathering.models import ScheduleHarvestVehicle, ScheduleHarvest
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from .models import (IncomingProduct, WeighingSet, Batch, FoodSafety, ProductPest, VehicleInspection, 
                     VehicleCondition, SampleCollection, SampleWeight, SamplePhysicalDamage, SampleDisease,
                     SampleResidue, SamplePest, Average)
from packhouses.catalogs.models import (ProductPest, ProductDisease, ProductPhysicalDamage, ProductResidue,)
from cities_light.models import City, Country, Region, SubRegion
from django.utils.text import capfirst
from datetime import datetime
from weasyprint import HTML, CSS
from django.template.loader import render_to_string
from io import BytesIO
from django.core import serializers
from django.http import JsonResponse
import json
from .resources import get_model_fields_verbose_names, transform_data
from .forms import ContainerInlineForm
from .utils import FILTER_DISPLAY_CONFIG, apply_filter_config
import qrcode, base64

def generate_qr_base64(data: str) -> str:
    qr = qrcode.make(data)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{img_str}"

def get_qr_for_batch(batch, request):
    url = request.build_absolute_uri(
        reverse("batch_record_report", args=[batch.uuid])
    )
    return generate_qr_base64(url)

def create_contenedor(request):
    if request.method == 'POST':
        form = ContainerInlineForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = ContainerInlineForm()
    return


def weighing_set_report(request, uuid, source="incoming"):
    if request.user.is_authenticated:
        user = str(request.user)
    else:
        user = None  
    # Redirige al login del admin usando 'reverse' si el usuario no está autenticado.
    if not request.user.is_authenticated:
        login_url = reverse('admin:login')
        return redirect(login_url)
    if source == "batch":
        batch = get_object_or_404(Batch, uuid=uuid)
        incomingProduct = batch.incomingproduct
    else:
        incomingProduct = get_object_or_404(IncomingProduct, uuid=uuid)
        batch = getattr(incomingProduct, 'batch', None)

    # Obtener Datos de la Organización
    if hasattr(request, 'organization'):
        organization = request.organization.organizationprofile.name
        add = request.organization.organizationprofile.address
        organization_profile = request.organization.organizationprofile

        def get_name(model, obj_id, default):
            if obj_id:
                try:
                    return model.objects.get(id=obj_id).name
                except model.DoesNotExist:
                    return f"{default} does not exist"
            return f"{default} not specified"

        # Obtener los nombres de las regiones
        city_name = get_name(SubRegion, organization_profile.city_id, "Ciudad")
        country_name = get_name(Country, organization_profile.country_id, "Country")
        state_name = get_name(Region, organization_profile.state_id, "State")
        district_name = get_name(City, organization_profile.district_id, "District")
        if organization_profile.logo:
            logo_url = organization_profile.logo.url
        else:
            logo_url = None

    pdf_title = _('Weighing Sets')
    packhouse_name = organization
    company_address = f"{add}, {district_name}, {city_name}, {state_name}, {country_name}"
    date = datetime.now()
    year = date.year

    # Obtener Corte relacionado con IncomingProduct
    harvest = ScheduleHarvest.objects.filter(incoming_product=incomingProduct).first()
    # Obtener pallets de IncomingProduct y transformar datos
    pallet_received_records = incomingProduct.weighingset_set.all()
    pallet_received_json = serializers.serialize('json', pallet_received_records)

    json_data = json.loads(pallet_received_json)
    if json_data:
        headers = list(json_data[0]['fields'].keys())
    else:
        headers = []

        # Excluir los campos no deseados
    excluded_fields = ['id', 'incoming_product', 'protected']
    headers = get_model_fields_verbose_names(WeighingSet, excluded_fields=excluded_fields)

    data = [[item['fields'].get(header) for header in headers] for item in json_data]
    # Transformar los datos del queryset
    data = transform_data(pallet_received_records, excluded_fields=excluded_fields)

    # Calcular los totales
    total_gross_weight = sum(item.gross_weight for item in pallet_received_records)
    total_net_weight = sum(item.net_weight for item in pallet_received_records)

    # Crear un diccionario con los totales usando gettext_lazy para traducción
    totals = {
        _('Total Gross Weight (Kg)'): total_gross_weight,
        _('Total Net Weight (Kg)'): total_net_weight,
    }

    # CSS
    base_url = request.build_absolute_uri('/')
    css = CSS(string='''
        @page {
            size: letter portrait;
        }''')

    # Renderizar el template HTML
    html_string = render_to_string('admin/packhouses/receiving/weighing-set-report.html', {
        'packhouse_name': packhouse_name,
        'company_address': company_address,
        'pdf_title': pdf_title,
        'logo_url': logo_url,
        'batch': batch,
        'harvest': harvest,
        'headers': headers,
        'data': data,
        "totals": totals,
        'year': year,
        'date': date,
        'printed_by': user,
    })

    # Convertir el HTML a PDF
    html = HTML(string=html_string, base_url=base_url)
    pdf_buffer = BytesIO()
    html.write_pdf(pdf_buffer, stylesheets=[css], )

    # Traducir el nombre del archivo manualmente
    filename = f"{_('weighing_set')}_{incomingProduct.id}.pdf"

    # Devolver el PDF como respuesta
    pdf_buffer.seek(0)
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response

def export_weighing_labels(request, uuid): 
    if request.user.is_authenticated:
        user = str(request.user)
    else:
        user = None  
    batch = get_object_or_404(Batch, uuid=uuid)
    weighing_sets = batch.incomingproduct.weighingset_set.all()

    organization_profile = batch.incomingproduct.scheduleharvest.orchard.organization.organizationprofile
    organization = organization_profile.name
    add = organization_profile.address
    
    def get_name(model, obj_id, default):
        if obj_id:
            try:
                return model.objects.get(id=obj_id).name
            except model.DoesNotExist:
                return f"{default} does not exist"
        return f"{default} not specified"

    city_name = get_name(SubRegion, organization_profile.city_id, "City")
    country_name = get_name(Country, organization_profile.country_id, "Country")
    state_name = get_name(Region, organization_profile.state_id, "State")
    district_name = get_name(City, organization_profile.district_id, "District")
    logo_url = organization_profile.logo.url if organization_profile.logo else None

    packhouse_name = organization
    company_address = f"{add}, {district_name}, {city_name}, {state_name}, {country_name}"
    date = datetime.now()
    year = str(date.year)

    # generar qr
    qr_code = get_qr_for_batch(batch, request) 

    base_url = request.build_absolute_uri('/')
    css = CSS(string='''
        @page {
            size: letter portrait;
        }''')
    
    html_string = render_to_string('admin/packhouses/receiving/weighing_labels.html', {
        'packhouse_name': packhouse_name,
        'company_address': company_address,
        'logo_url': logo_url,
        'batch': batch,
        'weighing_sets': weighing_sets,
        'year': year,
        'date': date,
        'printed_by': user,
        'qr_code': qr_code,
    })

    # Convertir el HTML a PDF
    html = HTML(string=html_string, base_url=base_url)
    pdf_buffer = BytesIO()
    html.write_pdf(pdf_buffer, stylesheets=[css],)

    # Traducir el nombre del archivo manualmente
    filename = f"{_('labels')}.pdf"

    # Devolver el PDF como respuesta
    pdf_buffer.seek(0)
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response

def basic_report(request, json_data, model_name, model_key, pretty_filters):
    if request.user.is_authenticated:
        user = str(request.user)
    else:
        user = None  
    # prepare data
    json_data = json.loads(json_data)
    base_url = request.build_absolute_uri('/')

    if json_data: 
        headers = list(json_data[0].keys()) 
    else: 
        headers = [] 
     
    data = [[item.get(header) for header in headers] for item in json_data]

    if hasattr(request, 'organization'):
        organization = request.organization.organizationprofile.name
        add =  request.organization.organizationprofile.address
        organization_profile = request.organization.organizationprofile
        def get_name(model, obj_id, default):
            if obj_id:
                try:
                    return model.objects.get(id=obj_id).name
                except model.DoesNotExist:
                    return f"{default} does not exist"
            return f"{default} not specified"

        # Obtener los nombres de las regiones
        city_name = get_name(SubRegion, organization_profile.city_id, "Ciudad")
        country_name = get_name(Country, organization_profile.country_id, "Country")
        state_name = get_name(Region, organization_profile.state_id, "State")
        district_name = get_name(City, organization_profile.district_id, "District")
        if organization_profile.logo:  
            logo_url = organization_profile.logo.url  
        else:
            logo_url = None
    pdf_title = model_name
    packhouse_name = organization
    company_address = f"{add}, {district_name}, {city_name}, {state_name}, {country_name}"
    columns_total = len(headers)
    date = datetime.now()
    year = str(date.year)
    ordered = apply_filter_config(pretty_filters, model_key)

    # 1. Separar “date‐ranges” del resto
    date_ranges = {}
    other_filters = {}
    for label, value in ordered.items():
        # Si el valor contiene " - ", asumimos que es un rango de fechas
        if isinstance(value, str) and " - " in value:
            date_ranges[label] = value
        else:
            other_filters[label] = value
    col_count = 4
    # orientation page
    if len(headers) < 10:
        css = CSS(string='''
        @page {
            size: letter portrait;
        }''')
        col_count = 3
    elif len(headers) < 16: 
        css = CSS(string='''
        @page {
            size: letter landscape;
        }''')
    else:
        css = CSS(string='''
        @page {
            size: 18in 11in;
        }''')

    # send data to create pdf
    html_string = render_to_string('admin/packhouses/base-table-report.html',{
        'company_info': 'Certiffy',
        'pdf_title': pdf_title,
        'headers': headers,
        'packhouse_name': packhouse_name,
        'company_address': company_address,
        'data': data,
        'columns_total': columns_total,
        'year': year,
        'date': date, 
        'printed_by': user,
        "date_ranges": date_ranges,
        "other_filters": other_filters,
        'col_count': col_count,
    })

    html = HTML(string=html_string, base_url=base_url)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{model_name}.pdf"'
    html.write_pdf(response, stylesheets=[css], )

    return response

def export_batch_record(request, uuid,):
    if request.user.is_authenticated:
        user = str(request.user)
    else:
        user = None  
    # === IDENTIFICACIÓN DEL LOTE E INOCUIDAD ===
    batch = get_object_or_404(Batch, uuid=uuid)
    foodsafety = getattr(batch, "foodsafety", None)

    # === DATOS DEL LOTE Y COSECHA ===
    harvest = getattr(batch.incomingproduct, "scheduleharvest", None)
    orchard_certifications = harvest.orchard.orchardcertification_set.all() if harvest and harvest.orchard else []
    crew = harvest.scheduleharvestharvestingcrew_set.all() if harvest else []
    scheduleharvestvehicle = harvest.scheduleharvestvehicle_set.all() if harvest else []

    # === ORGANIZACIÓN Y UBICACIÓN ===
    organization_profile = harvest.orchard.organization.organizationprofile if harvest else None
    organization = organization_profile.name if organization_profile else ""
    add = organization_profile.address if organization_profile else ""

    def get_name(model, obj_id, default):
        if obj_id:
            try:
                return model.objects.get(id=obj_id).name
            except model.DoesNotExist:
                return f"{default} does not exist"
        return f"{default} not specified"

    city_name = get_name(SubRegion, getattr(organization_profile, "city_id", None), "City")
    country_name = get_name(Country, getattr(organization_profile, "country_id", None), "Country")
    state_name = get_name(Region, getattr(organization_profile, "state_id", None), "State")
    district_name = get_name(City, getattr(organization_profile, "district_id", None), "District")
    logo_url = organization_profile.logo.url if organization_profile and organization_profile.logo else None

    # === DATOS DE INOCUIDAD ===
    drymatters = []
    product_pests = []
    internal_inspections = []
    vehicle_reviews = []
    vehicle_tables = []
    sample_tables = []
    damage_table_blocks = []
    total_samples = 0
    averages = average_dry_matter = average_internal_temp = acceptance_report = 0

    if foodsafety:
        # Subdatos relacionados con inocuidad
        drymatters = foodsafety.drymatter_set.all()
        batch = getattr(foodsafety, 'batch', None)
        incoming_product = getattr(batch, 'incomingproduct', None) if batch else None
        schedule = getattr(incoming_product, 'scheduleharvest', None) if incoming_product else None

        # === Plagas Por Producto ===
        if schedule and schedule.product:
            product_pests = ProductPest.objects.filter(product=schedule.product, pest__pest__inside=True)

        # === Inspecciones Internas ===
        internal_inspections = foodsafety.internalinspection_set.all()
        for ins in internal_inspections:
            ins.pest_ids = set(p.id for p in ins.product_pest.all())

        # === Revisión de Transporte ===
        vehicle_reviews = foodsafety.vehiclereview_set.prefetch_related(
            'vehicleinspection_set', 'vehiclecondition_set', 'vehicle__vehicle'
        )

        boolean_fields_inspection = [
            field for field in VehicleInspection._meta.fields
            if isinstance(field, models.BooleanField) and field.name != 'id'
        ]
        boolean_fields_condition = [
            field for field in VehicleCondition._meta.fields
            if isinstance(field, models.BooleanField) and field.name != 'id'
        ]

        for review in vehicle_reviews:
            inspections = review.vehicleinspection_set.all()
            conditions = review.vehiclecondition_set.all()

            if not inspections.exists() and not conditions.exists():
                continue

            inspection_data = [
                [
                    field.verbose_name,
                    "✅" if getattr(inspection, field.name) else '',
                    "❌" if not getattr(inspection, field.name) else ''
                ]
                for inspection in inspections
                for field in boolean_fields_inspection
            ] if inspections.exists() else []

            condition_data = [
                [
                    field.verbose_name,
                    "✅" if getattr(condition, field.name) else '',
                    "❌" if not getattr(condition, field.name) else ''
                ]
                for condition in conditions
                for field in boolean_fields_condition
            ] if conditions.exists() else []

            vehicle_tables.append({
                'vehicle': review.vehicle,
                'tables': [
                    {
                        'title': "Transport Inspection",
                        'headers': ["Transport Inspection", "Meets Standards", "Does Not Meet Standards"],
                        'data': inspection_data,
                    },
                    {
                        'title': "Transport Condition",
                        'headers': ["Transport Condition", "Meets Standards", "Does Not Meet Standards"],
                        'data': condition_data,
                    }
                ]
            })

        # === Criterios Sensoriales ===
        boolean_fields_samples = [
            field for field in SampleCollection._meta.fields
            if isinstance(field, models.BooleanField) and field.name != 'id'
        ]

        sample_collections = SampleCollection.objects.filter(food_safety=foodsafety)

        for sample in sample_collections:
            weights_qs = SampleWeight.objects.filter(sample_collection=sample)
            total_weights = weights_qs.count()
            weights_list = list(weights_qs.values_list("weight", flat=True))
            weights_list.sort()
            min_weight = weights_list[0] if weights_list else None
            max_weight = weights_list[-1] if weights_list else None


            sample_data = [
                [
                    field.verbose_name,
                    "✅" if getattr(sample, field.name) else "",
                    "❌" if not getattr(sample, field.name) else ""
                ]
                for field in boolean_fields_samples
            ]

            sample_tables.append({
                'sample': sample,
                'table': {
                    'title': "Sensory Criteria",
                    'headers': ["Sensory Criteria", "Yes", "No"],
                    'data': sample_data,
                },
                'min_weight': min_weight,
                'max_weight': max_weight,
                'total_weights': total_weights,
                'weights_list': weights_list,
            })

        total_samples = sum(item["total_weights"] for item in sample_tables)

        # === Tabla de Daños (dinámica con rowspan) ===
        damage_table_blocks = [
        {
            "label": _("Physical Damage"),
            "rows": [
                {
                    "description": product.name,
                    "quantity": related.sample_physical_damage if related else "",
                    "percentage": related.percentage if related else ""
                }
                for product in ProductPhysicalDamage.objects.filter(product=schedule.product)
                for related in [SamplePhysicalDamage.objects.filter(
                    sample_collection__in=sample_collections,
                    product_physical_damage=product
                ).first()]
            ]
        },
        {
            "label": _("Disease"),
            "rows": [
                {
                    "description": product.name,
                    "quantity": related.sample_disease if related else "",
                    "percentage": related.percentage if related else ""
                }
                for product in ProductDisease.objects.filter(product=schedule.product)
                for related in [SampleDisease.objects.filter(
                    sample_collection__in=sample_collections,
                    product_disease=product
                ).first()]
            ]
        },
        {
            "label": _("Residue"),
            "rows": [
                {
                    "description": product.name,
                    "quantity": related.sample_residue if related else "",
                    "percentage": related.percentage if related else ""
                }
                for product in ProductResidue.objects.filter(product=schedule.product)
                for related in [SampleResidue.objects.filter(
                    sample_collection__in=sample_collections,
                    product_residue=product
                ).first()]
            ]
        },
        {
            "label": _("Pest"),
            "rows": [
                {
                    "description": product.name,
                    "quantity": related.sample_pest if related else "",
                    "percentage": related.percentage if related else ""
                }
                for product in ProductPest.objects.filter(product=schedule.product)
                for related in [SamplePest.objects.filter(
                    sample_collection__in=sample_collections,
                    product_pest=product
                ).first()]
            ]
        },
    ]
        
        # === Promedios ===
        averages = Average.objects.filter(food_safety=foodsafety).first()
        average_dry_matter = averages.average_dry_matter if averages else None
        average_internal_temp = averages.average_internal_temperature if averages else None
        acceptance_report = averages.acceptance_report if averages and averages.acceptance_report else None

    # === CONTEXTO Y GENERACIÓN PDF ===
    packhouse_name = organization
    company_address = f"{add}, {district_name}, {city_name}, {state_name}, {country_name}"
    date = datetime.now()
    year = str(date.year)
    base_url = request.build_absolute_uri('/')
    css = CSS(string='@page { size: letter portrait; }')

    context = {
        'packhouse_name': packhouse_name,
        'company_address': company_address,
        'logo_url': logo_url,
        'year': year,
        'date': date,
        'printed_by': user,
        'batch': batch,
        'harvest': harvest,
        'crew': crew,
        'scheduleharvestvehicle': scheduleharvestvehicle,
        'orchard_certifications': orchard_certifications,
        'foodsafety': foodsafety,
        'drymatters': drymatters,
        'product_pests': product_pests,
        'internal_inspections': internal_inspections,
        'vehicle_tables': vehicle_tables,
        'sample_tables': sample_tables,
        'total_samples': total_samples,
        'damage_table_blocks': damage_table_blocks,
        'average_dry_matter': average_dry_matter,
        'average_internal_temperature': average_internal_temp,
        'acceptance_report': acceptance_report,
    }

    html_string = render_to_string('admin/packhouses/receiving/batch_record.html', context)
    pdf = HTML(string=html_string, base_url=base_url).write_pdf(stylesheets=[css])

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{_('batch_record')}.pdf"'
    return response



