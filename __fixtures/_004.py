from organizations.models import Organization
from common.profiles.models import PackhouseExporterProfile, PackhouseExporterSetting, OrganizationProfile
from cities_light.models import Country, Region, City
import json

orgs = ['poner aqui el json de los packhouseexporterprofile']
orgs = json.loads(orgs)

for item in orgs:
    fields = {k: v for k, v in item['fields'].items() if k not in ['products', 'polymorphic_ctype']}
    fields['organization'] = Organization.objects.get(id=fields['organization'])
    fields['country'] = Country.objects.get(id=fields['country'])
    fields['state'] = Region.objects.get(id=fields['state'])
    fields['city'] = City.objects.get(id=fields['city'])
    products = item['fields']['products']
    newp = PackhouseExporterProfile(**fields)
    newp.save()
    for i in products:
       newp.product_kinds.add(i)
    print("newp", newp)
