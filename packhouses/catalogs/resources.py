from import_export.fields import Field
from .models import (Market, Product, MarketProductSize, )
from django.http import HttpResponse
from common.base.utils import ExportResource, DehydrationResource, default_excluded_fields
from import_export import resources, fields
from django.utils.translation import gettext_lazy as _


class MarketResource(DehydrationResource, ExportResource):
    market_class_name = Field(column_name=_("Market Class"), attribute="marketclass_set", readonly=True)

    def dehydrate_market_class_name(self, market):
        market_classes = market.marketclass_set.all()  
        return ", ".join([mc.name for mc in market_classes]) if market_classes else None

    class Meta:
        model = Market
        exclude = tuple(default_excluded_fields + ("address_label",))


class ProductResource(DehydrationResource, ExportResource): 
    product_season = Field(column_name=_("Season"), readonly=True) 
    product_variety = Field(column_name=_("Variety"), readonly=True) 
    mass_volume_kind = Field(column_name=_("Mass Volume Kind"), readonly=True) 
    harvest_size_kind = Field(column_name=_("Harvest Size Kinds"), readonly=True) 

    def dehydrate_product_season(self, product):
        product_seasons = product.productseasonkind_set.all()  
        return  ", ".join([s.name for s in product_seasons]) if product_seasons else None
    
    def dehydrate_product_variety(self, product):
        product_varieties = product.productvariety_set.all()  
        return  ", ".join([pv.name for pv in product_varieties]) if product_varieties else None
    
    def dehydrate_mass_volume_kind(self, product):
        mass_volume = product.productmassvolumekind_set.all()  
        return  ", ".join([mvk.name for mvk in mass_volume]) if mass_volume else None
    
    def dehydrate_harvest_size_kind(self, product):
        harvest_size = product.productharvestsizekind_set.all()  
        return  ", ".join([phk.name for phk in harvest_size]) if harvest_size else None

    class Meta:
        model = Product
        exclude = tuple(default_excluded_fields + ("description",))

    
class MarketProductSizeResource(DehydrationResource, ExportResource):
    class Meta:
        model = MarketProductSize
        exclude = default_excluded_fields 
    

