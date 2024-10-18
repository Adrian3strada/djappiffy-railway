from django.contrib import admin
from .models import UserProfile, OrganizationProfile

# Register your models here.


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(OrganizationProfile)
class OrganizationProfileAdmin(admin.ModelAdmin):
    pass
