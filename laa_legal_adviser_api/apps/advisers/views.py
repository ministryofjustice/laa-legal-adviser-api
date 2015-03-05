from django.shortcuts import render
from django.views.generic import TemplateView


class Search(TemplateView):
    template_name = 'search.html'
