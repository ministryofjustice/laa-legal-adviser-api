from django.contrib.gis.geos import Point
from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework import viewsets

from .models import Location
from .serializers import LocationSerializer


class Search(TemplateView):
    template_name = 'search.html'


class AdviserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LocationSerializer

    def get_queryset(self):
        lon = self.request.query_params.get('lon')
        lat = self.request.query_params.get('lat')
        pnt = Point(-0.12776, 51.50735)

        try:
            pnt = Point(float(lon), float(lat))
        except (ValueError, TypeError):
            pass

        return Location.objects.all().distance(pnt).order_by('distance')
