from django.urls import path
from . import views  

urlpatterns = [
    path(
        'report/harvest-order/<int:harvest_id>/',
        views.harvest_order_pdf,
        name='harvest_order_pdf'
    ),
]
