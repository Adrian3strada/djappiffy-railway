from organizations.templatetags.org_tags import is_admin
from rest_framework import serializers
from .models import UserProfile, OrganizationProfile
from organizations.models import Organization, OrganizationOwner, OrganizationUser
from common.base.serializers import CountrySerializer
# from django_countries import countries
#


class UserProfileSerializer(serializers.ModelSerializer):
    # country = serializers.ChoiceField(choices=countries, required=False)
    # country_value = CountrySerializer(source='country', read_only=True)
    display_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserProfile
        fields = "__all__"

    def get_display_name(self, instance):
        """Retorna el valor del método __str__ del modelo."""
        return str(instance)

    """
    def to_representation(self, instance):
        # Override to return the readable country name.
        data = super().to_representation(instance)

        # Cambiar el código de país por el nombre del país
        if instance.country:
            data['country'] = instance.country.code
        else:
            data['country'] = None

        return data

    def create(self, validated_data):
        # Override to create the UserProfile with country code.
        country_code = validated_data.pop('country', None)
        user_profile = UserProfile(**validated_data)

        # Asignar el código de país (puede ser None si no se proporciona)
        if country_code:
            user_profile.country = country_code

        user_profile.save()
        return user_profile

    def update(self, instance, validated_data):
        # Override to update the UserProfile with country code.
        country_code = validated_data.pop('country', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Asignar el código de país (puede ser None si no se proporciona)
        if country_code:
            instance.country = country_code

        instance.save()
        return instance
    """


class OrganizationProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationProfile
        fields = "__all__"

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user

        # Crear la organización
        organization = Organization.objects.create(
            name=validated_data['name'],
            is_active=True
        )

        # Crear un OrganizationUser asociado al usuario y la organización
        organization_user = OrganizationUser.objects.create(
            organization=organization,
            user=user,
            is_admin=True
        )

        # Crear OrganizationOwner usando la instancia de OrganizationUser
        OrganizationOwner.objects.create(
            organization=organization,
            organization_user=organization_user
        )

        validated_data['organization'] = organization

        # Crear el OrganizationProfile y asociarlo a la organización
        organization_profile = OrganizationProfile.objects.create(
            **validated_data
        )

        return organization_profile
