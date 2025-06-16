# from django.core.management.base import BaseCommand
# from packhouses.receiving.models import Batch, IncomingProduct, FoodSafety, WeighingSet, WeighingSetContainer
# from packhouses.gathering.models import ScheduleHarvest, ScheduleHarvestHarvestingCrew, ScheduleHarvestVehicle, ScheduleHarvestContainerVehicle
# from packhouses.sales.models import Order, OrderItemWeight, OrderItem, OrderItemPackaging, OrderItemPallet, OrderItemPackagingProcess
# from packhouses.certifications.models import CertificationDocument, Certification
# from packhouses.purchases.models import Requisition, PurchaseOrder, ServiceOrder, PurchaseOrder
# from packhouses.storehouse.models import AdjustmentInventory, StorehouseEntry
# import random
# from django.utils import timezone
# from datetime import timedelta
# from packhouses.catalogs.models import (Market, ProductMarketClass, Client, Maquiladora, Product, ProductVariety,
#                                         ProductPhenologyKind, ProductPackaging, ProductPackagingPallet,
#                                         ProductSize, ProductRipeness, Market, Provider, Gatherer, Orchard, HarvestingCrew, Vehicle, 
#                                         OrchardCertification, Supply, ProductHarvestSizeKind, WeighingScale, Pallet, SizePackaging)
# from packhouses.catalogs.settings import CLIENT_KIND_CHOICES
# from common.base.models import Incoterm, LocalDelivery
# from organizations.models import Organization
# from common.profiles.models import OrganizationProfile
# from common.settings import STATUS_CHOICES
# from packhouses.sales.settings import ORDER_ITEMS_KIND_CHOICES, ORDER_ITEMS_PRICING_CHOICES
# from packhouses.catalogs.utils import  get_harvest_cutting_categories_choices

# def runOrder():
#     today = timezone.now().date()
#     organization = Organization.objects.get(id=1)
#     organization_data = OrganizationProfile.objects.get(organization=organization)

#     list_client_category = [key for key, _ in CLIENT_KIND_CHOICES]
#     list_status = [key for key, _ in STATUS_CHOICES if key != 'closed' and key != 'canceled']
#     list_order_items_local = [key for key, _ in ORDER_ITEMS_KIND_CHOICES]
#     list_order_items_incont = [key for key, _ in ORDER_ITEMS_KIND_CHOICES if key != 'product_weight']
#     list_order_pricing_local = [key for key, _ in ORDER_ITEMS_PRICING_CHOICES]
#     list_order_pricing_incont = [key for key, _ in ORDER_ITEMS_PRICING_CHOICES if key != 'product_weight']

#     ids_maquiladora = list(Maquiladora.objects.filter(organization=organization, is_enabled=True).values_list('id', flat=True))
#     ids_incoterm = list(Incoterm.objects.values_list('id', flat=True))
#     ids_localdelivery = list(LocalDelivery.objects.values_list('id', flat=True))

#     for i in range(150):
#         difference_days = random.randint(0, 30)
#         registration = today
#         created = today
#         shipment = today
#         delivery = today
#         client = None
#         maquiladora = None
#         local_delivery=None
#         incoterms=None
#         order_item = None
#         order_pricing = None
#         product = None
        
#         client_category = list_client_category[random.randint(0, len(list_client_category)-1)]

#         if difference_days > 10:      #Calcular Fechas
#             registration = today - timedelta(days=difference_days)
#             created = timezone.now() - timedelta(days=difference_days)
#             shipment = today - timedelta(days=difference_days - random.randint(0, 5))
#             delivery = today - timedelta(days=difference_days - random.randint(5, 10))
        
#         elif difference_days <=10 and difference_days > 0:
#             registration = today - timedelta(days=difference_days)
#             created = timezone.now() - timedelta(days=difference_days)
#             days_shipment = random.randint(0, difference_days)
#             difference_shipment = difference_days - days_shipment
#             shipment = today - timedelta(days=days_shipment)
            
#             if difference_shipment > 2:
#                 days_delivery = random.randint(0, difference_shipment)
#                 delivery = today - timedelta(days=days_delivery)
#             else:
#                 delivery = today + timedelta(days=random.randint(0, 10))
            
#         else:
#             additional_days = random.randint(0, 10)
#             shipment = today + timedelta(days=additional_days)
#             delivery = today + timedelta(days=(additional_days + random.randint(0, 10)))

#         if client_category == "packhouse":
#             ids_client = list(Client.objects.filter(category="packhouse", organization=organization, market_id__in=[1,3]).values_list('id', flat=True))
#             client = Client.objects.get(id=random.choice(ids_client))

#             if organization_data.country == client.market.country:
#                 local_delivery = LocalDelivery.objects.get(id=random.choice(ids_localdelivery))
#                 order_item = list_order_items_local[random.randint(0, len(list_order_items_local)-1)]
#                 order_pricing = list_order_pricing_local[random.randint(0, len(list_order_pricing_local)-1)]

#             else:
#                 incoterms = Incoterm.objects.get(id=random.choice(ids_incoterm))
#                 order_item = list_order_items_incont[random.randint(0, len(list_order_items_incont)-1)]
#                 order_pricing = list_order_pricing_incont[random.randint(0, len(list_order_pricing_incont)-1)]

#         else:
#             maquiladora = Maquiladora.objects.get(id=random.choice(ids_maquiladora))
#             client = maquiladora.clients.first()

#             if organization_data.country == client.market.country:
#                 local_delivery = LocalDelivery.objects.get(id=random.choice(ids_localdelivery))
#                 order_item = list_order_items_local[random.randint(0, len(list_order_items_local)-1)]
#                 order_pricing = list_order_pricing_local[random.randint(0, len(list_order_pricing_local)-1)]

#             else:
#                 incoterms = Incoterm.objects.get(id=random.choice(ids_incoterm))
#                 order_item = list_order_items_incont[random.randint(0, len(list_order_items_incont)-1)]
#                 order_pricing = list_order_pricing_incont[random.randint(0, len(list_order_pricing_incont)-1)]

#         ids_product = list(Product.objects.filter(organization=organization, markets__country=client.market.country, is_enabled=True).exclude(id__in=[2,3,5,6]).values_list('id', flat=True))
#         product = Product.objects.get(id=random.choice(ids_product))

#         ids_product_variety = list(ProductVariety.objects.filter(is_enabled=True, product=product).values_list('id', flat=True))
#         product_variety = ProductVariety.objects.get(id=random.choice(ids_product_variety))

#         obj_order = Order.objects.create(client_category=client_category,
#             maquiladora=maquiladora,
#             client=client,
#             local_delivery=local_delivery,
#             incoterms=incoterms,
#             registration_date= registration,
#             shipment_date=shipment,
#             delivery_date=delivery,
#             product=product,
#             product_variety=product_variety,
#             order_items_kind=order_item,
#             status=list_status[random.randint(0, len(list_status)-1)],
#             organization=organization,
#             created_at=created
#         )

#         obj_order.created_at = created
#         obj_order.save()

#         # Para los inlines
#         ids_phenology = ProductPhenologyKind.objects.filter(is_enabled=True, product=product).values_list('id', flat=True)
#         phenology = ProductPhenologyKind.objects.get(id=random.choice(ids_phenology))

#         ids_market_class = ProductMarketClass.objects.filter(is_enabled=True, product=product, market=client.market).values_list('id', flat=True)
#         market_class = ProductMarketClass.objects.get(id=random.choice(ids_market_class))
        
#         ids_ripeness = ProductRipeness.objects.filter(is_enabled=True, product=product).values_list('id', flat=True)
#         ripeness = ProductRipeness.objects.get(id=random.choice(ids_ripeness))

#         quantity = random.randint(10, 100)
#         unit_price = random.randint(10, 100)

#         if order_item == "product_weight":
#             ids_size = list(ProductSize.objects.filter(product=product, market=client.market).values_list('id', flat=True))
#             size = ProductSize.objects.get(id=random.choice(ids_size))
#             amount_price = quantity*unit_price

#             if size.name == "BORONA":
#                 phenology = None
#                 market_class = None

#             elif size.category in ['mix', 'waste', 'biomass']:
#                 phenology = None
#                 market_class = None
#                 ripeness = None

#             weight = OrderItemWeight.objects.create(
#                 product_size= size,
#                 product_phenology = phenology,
#                 product_market_class = market_class,
#                 product_ripeness = ripeness,
#                 quantity = quantity,
#                 amount_price = amount_price,
#                 unit_price = unit_price,
#                 order = obj_order
#             )

#         else:
#             ids_size = list(ProductSize.objects.filter(category="size", product=product, market=client.market).values_list('id', flat=True))
#             size = ProductSize.objects.get(id=random.choice(ids_size))

#             product_presentations_per_packaging = None
#             product_pieces_per_presentation = None
#             pallet_quantity = None
#             packaging_quantity = None
#             amount_price = None
#             product_packaging = None
#             product_packaging_pallet = None
#             category_packaging = None
#             ids_product_packaging = None

#             if size.name == "BORONA":
#                 phenology = None
#                 market_class = None

#             elif size.category in ['mix', 'waste', 'biomass']:
#                 phenology = None
#                 market_class = None
#                 ripeness = None

#             if order_pricing == "product_presentation":
#                 category_packaging = "presentation"
#                 pallet_quantity = random.randint(10, 100)
#                 amount_price = pallet_quantity*unit_price

#             ids_product_packaging = ProductPackaging.objects.filter(market=client.market, organization=organization, product=product, is_enabled=True).values_list('id', flat=True)
#             ids_product_packaging_pallet = Pallet.objects.filter(market=client.market, product=product, is_enabled=True, organization=organization,).values_list('id', flat=True)
#             product_packaging = ProductPackaging.objects.get(id=random.choice(ids_product_packaging))
#             product_packaging_pallet = Pallet.objects.get(id=random.choice(ids_product_packaging_pallet))
            
#             ids_size_packaging = SizePackaging.objects.filter(product_packaging=product_packaging, is_enabled=True, organization=organization,).values_list('id', flat=True)
#             size_packaging = SizePackaging.objects.get(id=random.choice(ids_size_packaging))

#             product_weight_per_packaging = random.randint(10, 20)
#             product_presentations_per_packaging = random.randint(10, 20)
#             product_pieces_per_presentation = random.randint(10, 20)

#             if order_item == "product_packaging":
#                 packaging_quantity = random.randint(10, 100)
#                 amount_price = packaging_quantity*unit_price

#             if order_item == "product_pallet":
#                 pallet_quantity = random.randint(10, 100)
#                 packaging_quantity = random.randint(10, 100)
#                 amount_price = pallet_quantity*packaging_quantity*unit_price

#             OrderItem.objects.create(
#                 pricing_by=order_pricing,
#                 product_weight_per_packaging=product_weight_per_packaging,
#                 product_presentations_per_packaging=product_presentations_per_packaging,
#                 product_pieces_per_presentation=product_pieces_per_presentation,
#                 pallet_quantity=pallet_quantity,
#                 packaging_quantity=packaging_quantity,
#                 amount_price = amount_price,
#                 unit_price = unit_price,
#                 order=obj_order,
#                 product_market_class=market_class,
#                 size_packaging = size,
#                 product_packaging=product_packaging,
#                 product_packaging_pallet=product_packaging_pallet,
#                 product_phenology=phenology,
#                 product_ripeness=ripeness,
#                 product_size=size_packaging,
#             )

# def runSchedule():
#     number_schedule = 30

#     organization = Organization.objects.get(id=1)
#     organization_data = OrganizationProfile.objects.get(organization=organization)
#     today = timezone.now().date()

#     list_status = None
#     list_harvest_category = [key for key, _ in get_harvest_cutting_categories_choices()]

#     ids_maquiladora = list(Maquiladora.objects.filter(organization=organization, is_enabled=True).values_list('id', flat=True))
#     ids_gatherer = list(Gatherer.objects.filter(organization=organization, is_enabled=True).values_list('id', flat=True))
#     ids_provider = list(Provider.objects.filter(organization=organization, category="product_provider", is_enabled=True).values_list('id', flat=True))
#     ids_product = list(Product.objects.filter(organization=organization, is_enabled=True).exclude(id__in=[2,3,5,6]).values_list('id', flat=True))
#     ids_weighing_scale = list(WeighingScale.objects.filter(organization=organization, is_enabled=True).values_list('id', flat=True))

#     for i in range(number_schedule):

#         # difference_days = None
#         # if i<(number_schedule/2):
#         #     difference_days = random.randint(30, 360)
#         # else:
#         #     difference_days = random.randint(0, 30)
#         difference_days = random.randint(0, 10)

#         harvest_date = today
#         created = today
#         category = None
#         product_provider=None
#         gatherer=None
#         maquiladora=None
#         product=None
#         product_variety=None
#         product_phenologies=None
#         product_harvest_size_kind=None
#         orchard=None
#         market=None
#         weight_expected=1
#         weighing_scale=None
#         meeting_point=None
#         status=None
#         comments=None
#         incoming_product=None

#         if difference_days > 15:      #Calcular Fechas
#             created = timezone.now() - timedelta(days=difference_days)
#             harvest_date = today - timedelta(days=(difference_days- random.randint(0, 15)))
#             list_status = [key for key, _ in STATUS_CHOICES if key != 'ready' and key != 'open']
#         elif difference_days <=15 and difference_days > 0:
#             created = timezone.now() - timedelta(days=difference_days)  
#             if difference_days > 2:
#                 list_status = [key for key, _ in STATUS_CHOICES] 
#                 harvest_date = today - timedelta(days=(difference_days- random.randint(0, difference_days)))
#             else:
#                 harvest_date = today + timedelta(days=random.randint(0, 10))
#                 list_status = [key for key, _ in STATUS_CHOICES if key != 'closed' and key != 'canceled']
#         else:
#             list_status = [key for key, _ in STATUS_CHOICES if key != 'closed' and key != 'canceled']
#             harvest_date = today + timedelta(days=random.randint(0, 10))

#         category = list_harvest_category[random.randint(0, len(list_harvest_category)-1)]
#         provider = Provider.objects.get(id=random.choice(ids_provider))
#         product = Product.objects.get(id=random.choice(ids_product))
#         weighing_scale = WeighingScale.objects.get(id=random.choice(ids_weighing_scale))
#         status = list_status[random.randint(0, len(list_status)-1)]
        
#         ids_orchard = list(Orchard.objects.filter(organization=organization, is_enabled=True, product=product).values_list('id', flat=True))
#         orchard = Orchard.objects.get(id=random.choice(ids_orchard))

#         ids_product_variety = list(ProductVariety.objects.filter(is_enabled=True, product=product).values_list('id', flat=True))
#         product_variety = ProductVariety.objects.get(id=random.choice(ids_product_variety))

#         ids_phenology = ProductPhenologyKind.objects.filter(is_enabled=True, product=product).values_list('id', flat=True)
#         phenology = ProductPhenologyKind.objects.get(id=random.choice(ids_phenology))

#         ids_harvest_size = ProductHarvestSizeKind.objects.filter(is_enabled=True, product=product).values_list('id', flat=True)
#         harvest_size = ProductHarvestSizeKind.objects.get(id=random.choice(ids_harvest_size))

#         ids_ripeness = ProductRipeness.objects.filter(is_enabled=True, product=product).values_list('id', flat=True)
#         ripeness = ProductRipeness.objects.get(id=random.choice(ids_ripeness))
        
#         markets_list = list(product.markets.filter(country__in=[158, 234]))
#         market = random.choice(markets_list) if markets_list else None


#         if category == "gathering":
#             gatherer = Gatherer.objects.get(id=random.choice(ids_gatherer))
#         elif category == "maquila":
#             maquiladora = Maquiladora.objects.get(id=random.choice(ids_maquiladora))

#         obj_schedule = ScheduleHarvest.objects.create(
#             harvest_date=harvest_date,
#             product_provider=provider,
#             category=category,
#             gatherer=gatherer,
#             maquiladora=maquiladora,
#             product=product,
#             product_variety=product_variety,
#             product_phenology=phenology,
#             product_harvest_size_kind=harvest_size,
#             product_ripeness = ripeness,
#             orchard=orchard,
#             market=market,
#             weight_expected=weight_expected,
#             weighing_scale=weighing_scale,
#             status=status,
#             organization=organization,
#             incoming_product=incoming_product
#         )

#         obj_schedule.created_at = created
#         obj_schedule.save()

#         # Para los inlines
#         number_harvest = random.randint(1, 3)
#         number_vehicle = random.randint(1, 3)
#         for j in range(number_harvest):
#             ids_provider_harvesting_crew = list(Provider.objects.filter(organization=organization, category="harvesting_provider", is_enabled=True).values_list('id', flat=True))
#             provider_harvesting_crew = Provider.objects.get(id=random.choice(ids_provider_harvesting_crew))
            
#             ids_harvesting_crew = list(HarvestingCrew.objects.filter(organization=organization, provider=provider_harvesting_crew, is_enabled=True).values_list('id', flat=True))
#             harvesting_crew = HarvestingCrew.objects.get(id=random.choice(ids_harvesting_crew))

#             obj_harvest_crew = ScheduleHarvestHarvestingCrew.objects.create(
#                 schedule_harvest=obj_schedule,
#                 provider=provider_harvesting_crew,
#                 harvesting_crew=harvesting_crew
#             )

#         for k in range(number_vehicle):
#             vehicle = None
#             guide_number = None 

#             ids_provider_harvesting_vehicle = list(Provider.objects.filter(organization=organization, category="harvesting_provider", is_enabled=True).values_list('id', flat=True))
#             provider_harvesting_vehicle = Provider.objects.get(id=random.choice(ids_provider_harvesting_vehicle))
#             vehicle_list = provider_harvesting_vehicle.vehicle_provider.all()
#             vehicle = random.choice(vehicle_list) if vehicle_list else None

#             obj_harvest_vehicle = ScheduleHarvestVehicle.objects.create(
#                 schedule_harvest=obj_schedule,
#                 provider=provider_harvesting_vehicle,
#                 vehicle=vehicle,
#                 guide_number=guide_number,
#                 stamp_number= "12345",
#                 has_arrived=False
#             )
            
#             ids_supply = list(Supply.objects.filter(organization=organization, kind__category="harvest_container", is_enabled=True).values_list('id', flat=True))
#             random_number_vehicle = random.randint(1, 3)

#             for x in range(random_number_vehicle):

#                 container = Supply.objects.get(id=random.choice(ids_supply))         
#                 quantity = random.choice(range(50, 101, 5))

#                 obj_container_vehicle = ScheduleHarvestContainerVehicle.objects.create(
#                     schedule_harvest_vehicle = obj_harvest_vehicle,
#                     harvest_container = container,
#                     quantity = quantity
#                 )

#                 weight_expected = quantity*container.capacity
#                 ScheduleHarvest.objects.filter(id=obj_schedule.id).update(weight_expected=weight_expected)

# def runIncoming():
#     organization = Organization.objects.get(id=1)
#     organization_data = OrganizationProfile.objects.get(organization=organization)
#     today = timezone.now().date()

#     ids_schedule_harvest = list(ScheduleHarvest.objects.filter(organization=organization).exclude(status__in=["open", "canceled"]).values_list('id', flat=True))

#     for schedule in ids_schedule_harvest:


#         list_status = None
#         status = "open"
#         is_quarantined = False
#         public_weight_result = 1
#         total_weighed_sets = 1

#         obj_incoming = IncomingProduct.objects.create(
#             status = status,
#             public_weighing_scale = None,
#             public_weight_result = public_weight_result,
#             weighing_record_number = "RN-12345",
#             total_weighed_sets = total_weighed_sets,
#             mrl = random.randint(5, 20),
#             phytosanitary_certificate = "PC-12345",
#             kg_sample = random.choice(range(0, 21, 5)),
#             is_quarantined = is_quarantined,
#             organization = organization,
#         )

#         obj_schedule = ScheduleHarvest.objects.get(id=schedule)
#         obj_schedule.incoming_product = obj_incoming
#         obj_schedule.save()

#         if obj_schedule.status == "closed":
#             list_status = [key for key, _ in STATUS_CHOICES if key != 'open' and key != 'ready']
#         else:
#             list_status = [key for key, _ in STATUS_CHOICES if key != 'closed' and key != 'canceled']

#         status_incoming = list_status[random.randint(0, len(list_status)-1)]
#         if status_incoming == "open":
#             is_quarantined = random.randint(0, 1)

#         if obj_schedule.weight_expected>1:
#             public_weight_result = random.choice(range(int(obj_schedule.weight_expected*0.80), int(obj_schedule.weight_expected), 30))
#         else:
#             public_weight_result = random.choice(range(1700, 3100, 100))

#         obj_incoming.created_at = obj_schedule.harvest_date
#         obj_incoming.public_weighing_scale = obj_schedule.weighing_scale
#         obj_incoming.status = status_incoming
#         obj_incoming.is_quarantined = is_quarantined
#         obj_incoming.public_weight_result = public_weight_result
#         obj_incoming.save()

#         # # Para los inlines 
#         # if is_quarantined == False and status_incoming != "canceled":

#         #     ids_harvesting_crews = list(ScheduleHarvestHarvestingCrew.objects.filter(schedule_harvest=obj_schedule).values_list('id', flat=True))
#         #     len_harvesting_crew = len(ids_harvesting_crews)

#         #     for harvesting_crews in ids_harvesting_crews:

#         #         harvesting_crew = ScheduleHarvestHarvestingCrew.objects.get(id=harvesting_crews)
#         #         gross_weight = public_weight_result/len_harvesting_crew
#         #         total_containers = 1
#         #         container_tare = 1
#         #         platform_tare = random.randint(1, 10)
#         #         net_weight = 1
#         #         protected = 1

#         #         obj_weighing = WeighingSet.objects.create(
#         #             harvesting_crew = harvesting_crew,
#         #             gross_weight = gross_weight,
#         #             total_containers = total_containers,
#         #             container_tare = container_tare,
#         #             platform_tare = platform_tare,
#         #             net_weight = net_weight,
#         #             protected = protected,
#         #             incoming_product = obj_incoming
#         #         )

#         #         ids_supply = list(Supply.objects.filter(organization=organization, kind__category="harvest_container", is_enabled=True).values_list('id', flat=True))
#         #         random_supplies = random.randint(1, 3)
#         #         quantity_container = 0

#         #         for x in range(random_supplies):

#         #             container = Supply.objects.get(id=random.choice(ids_supply))         
#         #             quantity = random.choice(range(50, 101, 5))
#         #             quantity_container += quantity

#         #             obj_weighing_container = WeighingSetContainer.objects.create(
#         #                 harvest_container = container,
#         #                 quantity = quantity,
#         #                 weighing_set = obj_weighing
#         #             )

#         #         obj_weighing.total_containers = quantity_container
#         #         obj_weighing.container_tare = quantity_container*(1/3)
#         #         obj_weighing.net_weight = gross_weight - quantity_container*(1/3) - platform_tare

#         #     ########################
#         #     ids_schedule_harvest_vehicle = list(ScheduleHarvestVehicle.objects.filter(schedule_harvest=obj_schedule).values_list('id', flat=True))
#         #     for schedule_harvest_vehicle in ids_schedule_harvest_vehicle:

#         #         obj_schedule_vehicle = ScheduleHarvestVehicle.objects.get(id=schedule_harvest_vehicle)
#         #         obj_schedule_vehicle.has_arrived = random.randint(0, 1)
#         #         obj_schedule_vehicle.save()
                
#         #         ids_container_vehicle = list(ScheduleHarvestContainerVehicle.objects.filter(schedule_harvest_vehicle=schedule_harvest_vehicle).values_list('id', flat=True))

#         #         for container_vehicle in ids_container_vehicle:
#         #             quantity = obj_container_vehicle.quantity
#         #             full_containers = 0
#         #             empty_containers = 0
#         #             missing_containers = 0

#         #             obj_container_vehicle = ScheduleHarvestContainerVehicle.get(id=container_vehicle)
                    
#         #             if status_incoming == "closed":
#         #                 full_containers = random.randint((quantity*0.75), quantity)
#         #                 empty_containers = quantity - full_containers
#         #             else:
#         #                 full_containers = random.randint((quantity/2), quantity)
#         #                 empty_containers = random.randint(0, (quantity/2))
#         #                 missing_containers = quantity - full_containers - empty_containers

#         #             obj_container_vehicle.full_containers = full_containers
#         #             obj_container_vehicle.empty_containers = empty_containers
#         #             obj_container_vehicle.missing_containers = missing_containers
#         #             obj_container_vehicle.save()

#         #         ids_supply = list(Supply.objects.filter(organization=organization, kind__category="harvest_container", is_enabled=True).values_list('id', flat=True))
#         #         random_number_vehicle = random.randint(0, 2)

#         #         for x in range(random_number_vehicle):

#         #             container = Supply.objects.get(id=random.choice(ids_supply))         
#         #             quantity = random.choice(range(50, 101, 5))

#         #             full_containers = 0
#         #             empty_containers = 0
#         #             missing_containers = 0
                    
#         #             if status_incoming == "closed":
#         #                 full_containers = random.randint((quantity*0.75), quantity)
#         #                 empty_containers = quantity - full_containers
#         #             else:
#         #                 full_containers = random.randint((quantity/2), quantity)
#         #                 empty_containers = random.randint(0, (quantity/2))
#         #                 missing_containers = quantity - full_containers - empty_containers

#         #             obj_container_vehicle_new = ScheduleHarvestContainerVehicle.objects.create(
#         #                 schedule_harvest_vehicle = obj_harvest_vehicle,
#         #                 harvest_container = container,
#         #                 quantity = quantity,
#         #                 full_containers = full_containers,
#         #                 empty_containers = empty_containers,
#         #                 missing_containers = missing_containers
#         #             )
        