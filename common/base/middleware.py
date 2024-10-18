# middleware.py

from django.utils import translation
from django.conf import settings


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
