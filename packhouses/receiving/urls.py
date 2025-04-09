from django.urls import path
from packhouses.receiving.views import pre_lot_weighing_report

app_name = 'receiving'

urlpatterns = [
    path('dadmin/receiving/incomingproduct/pre_lot_weighing_report/<int:pk>/', pre_lot_weighing_report, name='pre_lot_weighing_report'),
]
