from django.conf import settings
from django.urls import include, path, re_path
from django.contrib import admin

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from search import views as search_views
from packhouses.gathering.views import generate_pdf


urlpatterns = [
    # Admin URLs personalizadas
    path('dadmin/gathering/scheduleharvest/generate_pdf/<int:harvest_id>/', generate_pdf, name='generate_pdf'),
    # Admin URLs
    path("dadmin/", admin.site.urls),
    path("wadmin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),

    # Search functionality
    path("search/", search_views.search, name="search"),

    # App-specific URLs
    path("", include("common.base.urls")),
    path("", include("common.profiles.urls")),
    path("", include("common.producers.urls")),
    path("", include("common.importers.urls")),
    path("", include("common.exporters.urls")),
    path("", include("common.government.urls")),
    path("", include("common.billing.urls")),
    path("", include("packhouses.catalogs.urls")),
    path("", include("packhouses.packhouse_settings.urls")),
    path("", include("eudr.parcels.urls")),

    # Internationalization
    path("i18n/", include("django.conf.urls.i18n")),

    # CKEditor integration
    path("ckeditor5/", include("django_ckeditor_5.urls")),
    path("_nested_admin/", include("nested_admin.urls")),
]

# Add static and media files serving in debug mode
if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Add Wagtail page serving mechanism
urlpatterns += [
    # Catch-all pattern for Wagtail pages, placed last
    path("", include(wagtail_urls)),
]

