from django.urls import path
from .views import good_harvest_practices_format, harvest_order_pdf

urlpatterns = [
    path('report/harvest-order/<uuid:uuid>/', harvest_order_pdf, name='harvest_order_pdf'),
    path('dadmin/gathering/scheduleharvest/good_harvest_practices_format/<uuid:uuid>/', good_harvest_practices_format, name='good_harvest_practices_format'),
]
