from .base import *
import os
import ast

# SECURITY WARNING: ¡No usar modo DEBUG en producción!
DEBUG = ast.literal_eval(os.getenv("DEBUG", "False"))
DEBUG_PROPAGATE_EXCEPTIONS = True

INSTALLED_APPS += [
    'auditlog',
    # 'axes',
]

REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = ['rest_framework.renderers.JSONRenderer']

SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-r88yqg4^(z0&iu#fuj)%a8_8(qu9)a47xa#4$omr&2ihewhrad")

# SECURITY WARNING: ¡Establecer correctamente los hosts permitidos en producción!
ALLOWED_HOSTS = ast.literal_eval(os.getenv("ALLOWED_HOSTS", "[*]"))

# El servicio de correo electrónico se debe configurar correctamente en producción con un servicio SMTP válido
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = os.getenv("EMAIL_HOST", "localhost")
EMAIL_PORT = os.getenv("EMAIL_PORT", 25)
EMAIL_USE_TLS = ast.literal_eval(os.getenv("EMAIL_USE_TLS", "False"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", None)
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", None)

MIDDLEWARE += [
    'auditlog.middleware.AuditlogMiddleware',
    # 'axes.middleware.AxesMiddleware',
]

AUDITLOG_INCLUDE_ALL_MODELS = True

try:
    from .auth import *
except ImportError:
    logger.error("No se encontró el archivo auth en settings")
    raise ImportError("No se encontró el archivo auth en settings")

DJANGO_STORAGE_BACKEND = os.getenv("DJANGO_STORAGE_BACKEND", "local")
if DJANGO_STORAGE_BACKEND == "local":
    logger.info("Using local storage")
else:
    logger.info("Using Django Storages")
    try:
        from .storages import *
        STORAGES['default']['BACKEND'] = STORAGES_DEFAULT_BACKEND
        STORAGES['default']['OPTIONS'] = STORAGES_DEFAULT_OPTIONS
    except ImportError:
        logger.error("No storages settings file found")
        raise ImportError("No storages configuration file found")

# TEMPLATES[0]['DIRS'].append(os.path.join(PROJECT_DIR, 'templates_production'))

CACHE_MIDDLEWARE_KEY_PREFIX = os.getenv("CACHE_MIDDLEWARE_KEY_PREFIX", "fffy")
CACHES = ast.literal_eval(os.getenv("CACHES"))

AUTHENTICATION_BACKENDS = [
    # AxesStandaloneBackend should be the first backend in the AUTHENTICATION_BACKENDS list.
    # 'axes.backends.AxesStandaloneBackend',

    # Django ModelBackend is the default authentication backend.
    'django.contrib.auth.backends.ModelBackend',
]

AXES_LOCKOUT_PARAMETERS = ["ip_address", ["username", "user_agent"]]
AXES_HANDLER = 'axes.handlers.cache.AxesCacheHandler'
AXES_CACHE = 'default'
AXES_COOLOFF_TIME = 6

try:
    from .local import *
except ImportError:
    pass
