from django.conf import settings
import ee

"""
# Inicializar Earth Engine
try:
    credentials = ee.ServiceAccountCredentials(email=settings.EE_SERVICE_ACCOUNT_EMAIL, key_data=settings.EE_SERVICE_ACCOUNT_DATA)
    ee.Initialize(credentials)
except Exception as e:
    print("Error al inicializar Earth Engine: {}".format(str(e)))
    print("email: ", settings.EE_SERVICE_ACCOUNT_EMAIL)
    print("key_data: ", settings.EE_SERVICE_ACCOUNT_DATA)
"""
