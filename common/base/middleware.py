# middleware.py

from django.utils import translation
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import redirect
import re

from organizations.models import Organization, OrganizationUser

from common.profiles.models import PackhouseExporterProfile, PackhouseExporterSetting


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
        requested_hostname = self._get_request_hostname(request)

        if re.match(r'^/(dadmin|rest)/.*', request.path):
            ### Ask for Settings
            try:
                requested_settings = PackhouseExporterSetting.objects.get(
                    hostname=requested_hostname,
                )
            except PackhouseExporterSetting.DoesNotExist:
                print("PackhouseExporterSetting does not exist")
                raise Http404

            ### Ask for PackhouseExporterProfile
            try:
                requested_organization_profile = requested_settings.profile
            except PackhouseExporterProfile.DoesNotExist:
                print("PackhouseExporterProfile does not exist")
                raise Http404

            ### Ask for Organization
            try:
                # Verificar si existe Organization asociada al PackhouseExporterProfile
                requested_organization = Organization.objects.get(
                    id=requested_organization_profile.organization_id,
                )
                request.session['organization_id'] = requested_organization.id
                request.organization = requested_organization
                request.organization_settings = requested_settings
            except Organization.DoesNotExist:
                raise Http404

            if request.user.is_authenticated:
                if not self._is_user_allowed(request.user, requested_organization):
                    raise PermissionDenied
                # print("User is allowed")

        response = self.get_response(request)

        return response

    def _get_request_hostname(self, request):
        """
        Extract URL hostname from request.
        NOTE: host = hostname + port
        """

        request_host = request.get_host()
        request_hostname = request_host.split(':')[0]
        return request_hostname

    def _is_user_in_organization(self, user, organization):
        """
        Query if the 'User' is member of the 'Organization'
            using 'OrganizationUser' information.
        """

        return OrganizationUser.objects.filter(
            organization=organization,
            user=user,
        ).exists()

    def _is_user_allowed(self, user, organization):
        """
        A: self._is_user_in_organization(user, organization)
        B: user.is_active
        C: user.is_staff
        D: user.is_superuser

        - Allowed if: (A and B and C) or (D)
        - Denied if: not(A and B and C) and not(D)
        """
        return (self._is_user_in_organization(user, organization) and
                user.is_active and user.is_staff) or user.is_superuser

class AdjustUploadLimitsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.allowed_paths = settings.LARGE_UPLOAD_ALLOWED_PATH_URLS
        self.max_fields = settings.LARGE_UPLOAD_FIELD_LIMIT

    def __call__(self, request):
        if request.path in self.allowed_paths and request.method == "POST":
            request.META['DATA_UPLOAD_MAX_NUMBER_FIELDS'] = self.max_fields
        return self.get_response(request)