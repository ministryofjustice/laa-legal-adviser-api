from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework import viewsets

from .models import Office


class Search(TemplateView):
    template_name = 'search.html'


class AdviserViewSet(viewsets.ReadOnlyModelViewSet):
    model = Office


