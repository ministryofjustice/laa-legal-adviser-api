from rest_framework import serializers

from .models import Office


class OfficeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Office
        fields = ('organisation', 'account_number', 'telephone', 'location')
