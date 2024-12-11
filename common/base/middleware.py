# middleware.py

from django.utils import translation
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import Http404

from organizations.models import Organization, OrganizationUser

from common.profiles.models import OrganizationProfile


class LanguageDetectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Verificar si resolver_match no es None
        lang = None
        if request.resolver_match:
            # Verificar el parámetro 'lang' en la URL
            lang = request.resolver_match.kwargs.get('lang')

        # Si no hay parámetro, verificar la cabecera Accept-Language
        if not lang:
            lang = request.META.get('HTTP_ACCEPT_LANGUAGE')

        # Establecer el idioma
        if lang:
            # Extraer el código del idioma
            lang_code = lang.split(',')[0] if isinstance(lang, str) else lang
            translation.activate(lang_code)
            request.LANGUAGE_CODE = lang_code
        else:
            # Usar el idioma por defecto si no se detecta
            lang_code = settings.LANGUAGE_CODE
            translation.activate(lang_code)
            request.LANGUAGE_CODE = lang_code

        response = self.get_response(request)
        return response


class SubdomainDetectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_host = self._get_request_host(request)

        try:
            # Verificar si existe OrganizationProfile asociada al HOST
            requested_organization_profile = OrganizationProfile.objects.get(host_full_name=request_host)
            try:
                # Verificar si existe Organization asociada al OrganizationProfile
                requested_organization = Organization.objects.get(id=requested_organization_profile.organization_id)
            except Organization.DoesNotExist:
                raise Http404
        except OrganizationProfile.DoesNotExist:
            raise Http404

        if request.user.is_authenticated:
            if self._is_user_in_organization(request.user, requested_organization) or request.user.is_staff :
                pass
            else:
                raise PermissionDenied
        else:
            raise PermissionDenied

        response = self.get_response(request)

        return response

    def _get_request_host(self, request):
        """
        Extract URL host from request without port.
        """
        request_full_host = request.get_host()
        request_host_only = request_full_host.split(':')[0]

        return request_host_only

    def _is_user_in_organization(self, user, organization):
        """
        Query if an User is member of some Organization.
        """

        return OrganizationUser.objects.filter(organization_id=organization.id, user_id=user.username).exists()
