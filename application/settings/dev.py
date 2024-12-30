import ast
import os
import logging
from .base import *

logging.basicConfig(level=logging.INFO)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = ast.literal_eval(os.getenv("DEBUG", "True"))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-r88yqg4^(z0&iu#fuj)%a8_8(qu9)a47xa#4$omr&2ihewhrad")

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ast.literal_eval(os.getenv("ALLOWED_HOSTS", "['*']"))

# CORS_ALLOW_ALL_ORIGINS = ast.literal_eval(os.getenv("CORS_ALLOW_ALL_ORIGINS", "True"))
CORS_ALLOW_ALL_ORIGINS = True

EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")

# Installed apps needed for development environment
INSTALLED_APPS.insert(0, 'whitenoise.runserver_nostatic')
INSTALLED_APPS += [
    'drf_spectacular',
]

if ast.literal_eval(os.getenv("DEV_USE_AUDITLOG", "False")):
    INSTALLED_APPS += ['auditlog']
    MIDDLEWARE += ['auditlog.middleware.AuditlogMiddleware']
    logger.info("Se encontró DEV_USE_AUDITLOG en True en las variables de entorno")

# Default authentication classes for DRF, these are no recommended for production for security concerns
REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] += [
    'rest_framework.authentication.SessionAuthentication',
    'rest_framework.authentication.BasicAuthentication',
]

try:
    from .auth import *
except ImportError:
    logger.error("No se encontró el archivo auth en settings")
    raise ImportError("No se encontró el archivo auth en settings")

DJANGO_STORAGE_BACKEND = os.getenv("DJANGO_STORAGE_BACKEND", "local")
if DJANGO_STORAGE_BACKEND == "local":
    # logger.info("Using local storage")
    pass
else:
    logger.info(f"Using Django Storages backend: {DJANGO_STORAGE_BACKEND}")
    try:
        from .storages import *
        STORAGES['default']['BACKEND'] = STORAGES_DEFAULT_BACKEND
        STORAGES['default']['OPTIONS'] = STORAGES_DEFAULT_OPTIONS
    except ImportError:
        logger.error("No storages settings file found")
        RUN = False
        raise ImportError("No storages configuration file found")

try:
    from .local import *
except ImportError:
    pass
