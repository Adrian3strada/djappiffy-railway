from django.conf import settings
from django.urls import include, path, re_path
from django.contrib import admin

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from search import views as search_views
from packhouses.gathering.views import (harvest_order_pdf, good_harvest_practices_format, cancel_schedule_harvest,
                                        set_scheduleharvest_ready)
from packhouses.purchases.views import (requisition_pdf, set_requisition_ready, purchase_order_supply_pdf,
                                        set_purchase_order_supply_ready, set_purchase_order_supply_open,
                                        set_purchase_order_supply_payment)
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    # Admin URLs personalizadas
    path('dadmin/gathering/scheduleharvest/harvest_order_pdf/<int:harvest_id>/', harvest_order_pdf,
         name='harvest_order_pdf'),
    path('dadmin/gathering/scheduleharvest/good_harvest_practices_format/<int:harvest_id>/',
         good_harvest_practices_format,
         name='good_harvest_practices_format'),
    path('dadmin/gathering/scheduleharvest/cancel_schedule_harvest/<int:pk>/', cancel_schedule_harvest,
         name='cancel_schedule_harvest'),
    path('dadmin/purchases/requisition_pdf/<int:requisition_id>/', requisition_pdf, name='requisition_pdf'),
    path('dadmin/purchases/set_requisition_ready/<int:requisition_id>/', set_requisition_ready,
         name='set_requisition_ready'),
    path('dadmin/purchases/purchase_order_supply_pdf/<int:purchase_order_supply_id>/', purchase_order_supply_pdf,
         name='purchase_order_supply_pdf'),
    path('dadmin/purchases/set_purchase_order_supply_ready/<int:purchase_order_supply_id>/',
         set_purchase_order_supply_ready,
         name='set_purchase_order_supply_ready'),
    path('dadmin/gathering/scheduleharvest/set_scheduleharvest_ready/<int:harvest_id>/', set_scheduleharvest_ready,
         name='set_scheduleharvest_ready'),
    path('dadmin/purchases/set_purchase_order_supply_open/<int:purchase_order_supply_id>/',
         set_purchase_order_supply_open,
         name='set_purchase_order_supply_open'),
    path('dadmin/purchases/set_purchase_order_supply_payment/<int:purchase_order_supply_id>/',
         set_purchase_order_supply_payment,
         name='set_purchase_order_supply_payment'),
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
    path("", include("packhouses.storehouse.urls")),
    path("", include("eudr.parcels.urls")),

    # Internationalization
    path("i18n/", include("django.conf.urls.i18n")),

    # CKEditor integration
    path("ckeditor5/", include("django_ckeditor_5.urls")),
    path("_nested_admin/", include("nested_admin.urls")),
    path("", include('packhouses.purchases.urls'))
]

# Add static and media files serving in debug mode
if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    urlpatterns += [
        # YOUR PATTERNS
        path('oas/schema/', SpectacularAPIView.as_view(), name='schema'),
        # Optional UI:
        path('oas/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        path('oas/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    ]

# Add Wagtail page serving mechanism
urlpatterns += [
    # Catch-all pattern for Wagtail pages, placed last
    path("", include(wagtail_urls)),
]
