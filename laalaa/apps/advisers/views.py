from django.db.models import Q
import re

from django import forms
from django.contrib.gis.geos import Point
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from rest_framework import exceptions, viewsets, filters
from rest_framework.views import exception_handler

from . import geocoder
from .importer import Import
from .models import Location
from .serializers import LocationOfficeSerializer


def custom_exception_handler(exc):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc)

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data['error'] = response.data['detail']
        del response.data['detail']

    return response


class CategoryFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        queryset = queryset.exclude(point__isnull=True).distinct()

        category_code = request.query_params.get('category')
        if category_code:
            category_code = category_code.upper()
            return queryset.filter(
                Q(office__categories__code=category_code) |
                Q(outreachservice__categories__code=category_code))

        return queryset


class MultipleCategoryFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):

        category_codes = request.query_params.getlist('categories')
        if category_codes:
            category_codes = [c.upper() for c in category_codes]
            return queryset.filter(
                Q(office__categories__code__in=category_codes) |
                Q(outreachservice__categories__code__in=category_codes))

        return queryset


class OrganisationTypeFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):

        organisation_type_names = request.query_params.getlist(
            'organisation_types')
        if organisation_type_names:
            return queryset.filter(
                Q(office__organisation__type__name__in=
                  organisation_type_names) |
                Q(outreachservice__office__organisation__type__name__in=
                  organisation_type_names))

        return queryset


class OrganisationNameFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):

        organisation_name = request.query_params.get('organisation_name')
        if organisation_name:
            return queryset.filter(
                Q(office__organisation__name__icontains=organisation_name) |
                Q(outreachservice__office__organisation__name__icontains=
                  organisation_name))

        return queryset


def format_postcode(postcode):
    postcode = re.sub(r"\s+", "", postcode)
    return re.sub(r'^(.*)(\d\w\w)', '\\1 \\2', postcode).upper()


class AdviserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LocationOfficeSerializer
    filter_backends = (CategoryFilter, MultipleCategoryFilter,
                       OrganisationTypeFilter, OrganisationNameFilter)

    def __init__(self, **kwargs):
        super(AdviserViewSet, self).__init__(**kwargs)
        self.origin = None

    def get_origin_postcode(self):
        postcode = self.request.query_params.get('postcode')
        if not postcode:
            return None

        try:
            result = geocoder.geocode(postcode)
            if hasattr(result, 'postcode'):
                postcode = result.postcode
            point = Point(result.longitude, result.latitude)
            self.origin = {
                'postcode': format_postcode(postcode),
                'point': {
                    'type': 'Point',
                    'coordinates': [point.x, point.y]}}
            return point
        except geocoder.GeocoderError:
            raise exceptions.ParseError('Postcode not found')

    def get_origin_point(self):
        try:
            point_param = self.request.query_params.get('point')
            if point_param:
                point = Point(*map(float, point_param.split(',')))
                self.origin = {
                    'postcode': None,
                    'point': {
                        'type': 'Point',
                        'coordinates': [point.x, point.y]}}
                return point
        except ValueError:
            raise exceptions.ParseError(
                'point parameter must be a lon,lat coordinate')

    def get_queryset(self):
        queryset = Location.objects.filter(
            Q(outreachservice__isnull=False) | Q(office__isnull=False)
        )

        origin = self.get_origin_point() or self.get_origin_postcode()
        if origin:
            return queryset.distance(
                origin, field_name='point').order_by('distance')

        return queryset

    def list(self, request, *args, **kwargs):
        response = super(AdviserViewSet, self).list(request, *args, **kwargs)
        response.data['origin'] = self.origin
        return response


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
                try:
                    importer = Import(
                        request.FILES['xlfile'].temporary_file_path())
                    importer.start()

                except Import.Balk:
                    messages.error(request, 'Import already in progress')

                except Import.Fail:
                    messages.error(request, 'Import failed')

                else:
                    messages.success(request, 'Import started')

            return redirect('/admin/import-in-progress/')
    return render(request, 'upload.html', {'form': form})


def import_progress(request):
    global importer
    if importer is not None:
        return JsonResponse(importer.thread.progress)
    return JsonResponse({'status': 'not running'})
