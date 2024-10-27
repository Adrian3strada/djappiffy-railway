from django.urls import path
from . import views

urlpatterns = [
    path(r'market_standard_product_size/<int:market_id>/', views.get_market_standard_product_size, name='get_market_standard_product_size'),
]
