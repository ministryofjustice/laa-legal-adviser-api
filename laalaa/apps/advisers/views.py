import logging

from django import forms
from django.contrib.gis.geos import Point
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from rest_framework import viewsets

from .importer import ImportProcess
from .models import Location
from .serializers import LocationSerializer


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


importer = None


class UploadSpreadsheetForm(forms.Form):
    xlfile = forms.FileField(label="Spreadsheet")


def upload_spreadsheet(request):
    global importer
    form = UploadSpreadsheetForm()
    if request.method == 'POST':
        form = UploadSpreadsheetForm(request.POST, request.FILES)
        if form.is_valid():
            if importer is None:
                importer = ImportProcess(
                    request.FILES['xlfile'].temporary_file_path())
                importer.start()
            return redirect('/admin/import-in-progress/')
    return render(request, 'upload.html', {'form': form})


def import_progress(request):
    global importer
    if importer is not None:
        return JsonResponse(importer.progress)
    return JsonResponse({'status': 'not running'})
