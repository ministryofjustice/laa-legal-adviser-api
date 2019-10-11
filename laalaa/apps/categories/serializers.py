from rest_framework import serializers

from advisers.models import Category


class CategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField()

    class Meta:
        model = Category
        fields = ["code", "civil", "name"]
