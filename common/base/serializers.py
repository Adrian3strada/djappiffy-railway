from rest_framework import serializers
from django.utils import translation
from .models import Product
from cities_light.models import City

#


class CountrySerializer(serializers.Serializer):
    code = serializers.CharField()
    name = serializers.CharField()


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        current_lang = translation.get_language()

        # Si el idioma está activado y existe un campo traducido para ese idioma, devolver solo ese campo
        name_field = f'name_{current_lang}'

        if name_field in representation and representation[name_field]:
            return {
                'id': representation['id'],
                'name': representation[name_field],
            }

        # Si no hay un idioma seleccionado o el campo traducido no existe, devolver todos
        return representation

    class Meta:
        model = Product
        fields = "__all__"

