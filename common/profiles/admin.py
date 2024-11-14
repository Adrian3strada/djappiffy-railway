from django.contrib import admin
from .models import (UserProfile, OrganizationProfile, ProducerProfile, ImporterProfile, PackhouseExporterProfile,
                     TradeExporterProfile)

# Register your models here.


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(OrganizationProfile)
class OrganizationProfileAdmin(admin.ModelAdmin):
    pass


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
