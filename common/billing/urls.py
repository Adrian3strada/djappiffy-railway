from django.urls import path, include
from common.base.router import drf_router
from .viewsets import LegalEntityCategoryViewSet

# write your urls here

urlpatterns = []

drf_router.register(r'rest/v1/billing/legal-entity-category', LegalEntityCategoryViewSet, basename='legalentitycategory')

