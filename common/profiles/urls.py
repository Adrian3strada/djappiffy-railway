from base.router import drf_router
from .viewsets import UserProfileViewSet, OrganizationProfileViewSet

# write your urls here

drf_router.register(r'rest/v1/profiles/user-profiles', UserProfileViewSet, basename='user-profiles')
drf_router.register(r'rest/v1/profiles/organization-profiles', OrganizationProfileViewSet, basename='organization-profiles')

urlpatterns = drf_router.urls
