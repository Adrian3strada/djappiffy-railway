from django.http import JsonResponse
from .models import MarketStandardProductSize

# Create your views here.


def get_market_standard_product_size(request, market_id):
    market_standard_product_sizes = MarketStandardProductSize.objects.filter(market_id=market_id).values('id', 'name')
    return JsonResponse(list(market_standard_product_sizes), safe=False)
