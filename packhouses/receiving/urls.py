from django.urls import path
from packhouses.receiving.views import weighing_set_report

app_name = 'receiving'

urlpatterns = [
    path('dadmin/receiving/incomingproduct/weighing_set_report/<int:pk>/', weighing_set_report, name='weighing_set_report'),
]
