from rest_framework import viewsets

from .serializers import CategorySerializer
from advisers.models import Category


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.filter()
    pagination_class = None
