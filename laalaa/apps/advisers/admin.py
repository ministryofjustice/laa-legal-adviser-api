from django.contrib import admin
from django.db.models import Q

from .models import Location, Office


class LocationTypeFilter(admin.SimpleListFilter):
    title = 'location type'

    parameter_name = 'location_type'

    def lookups(self, request, model_admin):
        return (
            ('office', 'Office'),
            ('pt', 'Part Time Location'),
            ('outreach', 'Outreach Location')
        )

    def queryset(self, request, queryset):
        if self.value() == 'office':
            return queryset.filter(office__isnull=False)
        if self.value() == 'pt':
            return queryset.filter(
                outreachservice__type__name='Part Time Location')
        if self.value() == 'outreach':
            return queryset.filter(
                outreachservice__type__name='Outreach Location')
        return queryset


class OfficeInline(admin.StackedInline):
    model = Office
    exclude = ('organisation',)
    can_delete = False
    max_num = 1
    extra = 0


class LocationAdmin(admin.ModelAdmin):
    exclude = ('point',)
    inlines = [OfficeInline]
    list_display = ('organisation', '__str__', 'location_type')
    list_display_links = ('__str__',)
    list_filter = (LocationTypeFilter,)
    search_fields = ('address', 'city', 'postcode')

    def get_search_results(self, request, queryset, term):
        queryset, use_distinct = super(LocationAdmin, self).get_search_results(
            request, queryset, term)
        queryset |= self.model.objects.filter(
            Q(office__organisation__name__icontains=term) |
            Q(outreachservice__office__organisation__name__icontains=term))
        return queryset, use_distinct


admin.site.register(Location, LocationAdmin)
