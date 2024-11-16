from django.conf import settings
import ee

try:
    credentials = ee.ServiceAccountCredentials(email=settings.EE_SA_EMAIL, key_file=settings.EE_SA_FILE)
    ee.Initialize(credentials)
except Exception as e:
    print("Error al inicializar Earth Engine: {}".format(str(e)))
