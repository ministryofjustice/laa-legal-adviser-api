from rest_framework import serializers
from rest_framework_gis import serializers as gis_serializers

from .models import Location


class DistanceField(serializers.ReadOnlyField):
    def to_representation(self, obj):
        # miles
        return obj.mi


class LocationSerializer(gis_serializers.GeoModelSerializer):
    distance = DistanceField()

    class Meta:
        model = Location
        fields = (
            'address', 'city', 'postcode', 'point', 'organisation',
            'location_type', 'distance')
