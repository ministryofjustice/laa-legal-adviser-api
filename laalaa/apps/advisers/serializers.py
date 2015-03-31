from rest_framework import serializers
from rest_framework_gis import serializers as gis_serializers

from .models import Location, Office, Organisation


class DistanceField(serializers.ReadOnlyField):
    def to_representation(self, obj):
        # miles
        return obj.mi


class OrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organisation
        fields = ('name', 'website',)


class LocationSerializer(gis_serializers.GeoModelSerializer):
    class Meta:
        model = Location
        fields = (
            'address', 'city', 'postcode', 'point', 'type')


class OfficeSerializer(gis_serializers.GeoModelSerializer):
    location = LocationSerializer()
    organisation = OrganisationSerializer()
    distance = DistanceField()

    class Meta:
        model = Office
        fields = (
            'telephone', 'location', 'organisation', 'distance')
