from django.urls import path
from packhouses.receiving.views import weighing_set_report, export_weighing_labels, export_batch_record
from common.base.router import drf_router
from .viewsets import BatchViewSet


urlpatterns = [
    path('dadmin/receiving/weighing_set_report/<uuid:uuid>/', weighing_set_report, name='weighing_set_report'),
    path('dadmin/receiving/batch/weighing_set_report/<uuid:uuid>/', weighing_set_report, {'source': 'batch'}, name='batch_weighing_set_report'),
    path('dadmin/receiving/batch/weighing_labels/<uuid:uuid>/', export_weighing_labels, name='weighing_set_labels'),
    path('receiving/batch/batch_record/<uuid:uuid>/', export_batch_record, name='batch_record_report'),
    path('receiving/food_safety/batch_record/<uuid:uuid>/', export_batch_record, name='food_safety_record_report'),
]

drf_router.register(r'rest/v1/receiving/batch', BatchViewSet, basename='batch')

urlpatterns += drf_router.urls


