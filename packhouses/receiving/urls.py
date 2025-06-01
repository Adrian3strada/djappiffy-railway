from django.urls import path
from common.base.router import drf_router
from packhouses.receiving.views import weighing_set_report


app_name = 'receiving'  # TODO: preguntar a Jaqueline ¿qué hace esto?

urlpatterns = [
    path('dadmin/receiving/incomingproduct/weighing_set_report/<int:pk>/', weighing_set_report, name='weighing_set_report'),
]

drf_router.register(r'rest/v1/receiving/batch', BatchViewSet, basename='batch')

urlpatterns += drf_router.urls
