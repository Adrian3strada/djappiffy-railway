from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django_countries import countries
from .serializers import CountrySerializer
from rest_framework.permissions import AllowAny
from django.utils import translation

# Create your views here.


class CountryListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, lang=None):
        # Establecer el idioma según el parámetro 'lang' o la configuración predeterminada
        if lang:
            translation.activate(lang)
        else:
            lang = translation.get_language()

        country_list = [{"code": code, "name": name} for code, name in countries]
        serializer = CountrySerializer(country_list, many=True)
        return Response(serializer.data)
