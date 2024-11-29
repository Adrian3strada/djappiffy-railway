from django.contrib import admin

from .models import (UserProfile, OrganizationProfile, ProducerProfile,
                     ImporterProfile, PackhouseExporterProfile,
                     TradeExporterProfile)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "first_name", "last_name", "phone_number",
                    "country"]
    ordering = ["user"]


@admin.register(OrganizationProfile)
class OrganizationProfileAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "host_full_name", "organization"]
    ordering = ["id"]


@admin.register(ProducerProfile)
class ProducerProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(ImporterProfile)
class ImporterProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(PackhouseExporterProfile)
class PackhouseExporterProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(TradeExporterProfile)
class TradeExporterProfileAdmin(admin.ModelAdmin):
    pass
