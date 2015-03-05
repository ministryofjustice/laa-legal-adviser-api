from rest_framework import serializers

from .models import office


class OfficeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Office
        fields = ('address', 'city', 'postcode', 'phone', 'lat', 'lon')
