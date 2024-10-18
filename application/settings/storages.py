import os
import ast
import logging
import json
from google.oauth2 import service_account

storages_logger = logging.getLogger(__name__)
storages_logger.info("Mostrando log de storages settings")

# Default storage settings, with the staticfiles storage updated.
# See https://docs.djangoproject.com/en/5.0/ref/settings/#std-setting-STORAGES
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    # ManifestStaticFilesStorage is recommended in production, to prevent
    # outdated JavaScript / CSS assets being served from cache
    # (e.g. after a Django upgrade).
    # See https://docs.djangoproject.com/en/5.0/ref/contrib/staticfiles/#manifeststaticfilesstorage
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DJANGO_STORAGE_BACKEND = os.getenv("DJANGO_STORAGE_BACKEND", "local")

STORAGES_STATICFILES_BACKEND = os.getenv("STORAGES_STATICFILES_BACKEND", "whitenoise.storage.CompressedManifestStaticFilesStorage")
# Para desarrollo usar STORAGES_STATICFILES_BACKEND=whitenoise.storage.CompressedStaticFilesStorage como variable de entorno

STORAGES['staticfiles']['BACKEND'] = STORAGES_STATICFILES_BACKEND

if DJANGO_STORAGE_BACKEND == "google":
    credentials = service_account.Credentials.from_service_account_info(json.loads(os.getenv("GS_CREDENTIALS")))
    STORAGES_DEFAULT_BACKEND = "storages.backends.gcloud.GoogleCloudStorage"
    STORAGES_DEFAULT_OPTIONS = {
        "bucket_name": os.getenv("GS_BUCKET_NAME", ""),
        "project_id": os.getenv("GS_PROJECT_ID", ""),
        "gzip": ast.literal_eval(os.getenv("GS_IS_GZIPPED", "False")),
        "gzip_content_types": os.getenv("GZIP_CONTENT_TYPES", "text/css,text/javascript,application/javascript,application/x-javascript,image/svg+xml").split(','),
        "credentials": credentials,
        "default_acl": ast.literal_eval(os.getenv("GS_DEFAULT_ACL", "None")),
        "querystring_auth": ast.literal_eval(os.getenv("GS_QUERYSTRING_AUTH", "True")),
        "file_overwrite": ast.literal_eval(os.getenv("GS_FILE_OVERWRITE", "True")),
        "max_memory_size": int(os.getenv("GS_MAX_MEMORY_SIZE", 0)),
        "blob_chunk_size": int(os.getenv("GS_BLOB_CHUNK_SIZE")) if os.getenv("GS_BLOB_CHUNK_SIZE") is not None else None,
        "object_parameters": ast.literal_eval(os.getenv("GS_OBJECT_PARAMETERS", "{}")),
        "custom_endpoint": os.getenv("GS_CUSTOM_ENDPOINT", None),
        "location": os.getenv("GS_LOCATION", ""),
    }
