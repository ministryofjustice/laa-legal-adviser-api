from django.urls import re_path
from django.contrib import admin
from django.db.models import Q
from django.views.generic import TemplateView

from .models import Office
from . import views


class LocationTypeFilter(admin.SimpleListFilter):
    title = "location type"

    parameter_name = "type"

    def lookups(self, request, model_admin):
        return (("office", "Office"), ("pt", "Part Time Location"), ("outreach", "Outreach Location"))

    def queryset(self, request, queryset):
        if self.value() == "office":
            return queryset.filter(office__isnull=False)
        if self.value() == "pt":
            return queryset.filter(outreachservice__type__name="Part Time Location")
        if self.value() == "outreach":
            return queryset.filter(outreachservice__type__name="Outreach Location")
        return queryset


class OfficeInline(admin.StackedInline):
    model = Office
    exclude = ("organisation",)
    can_delete = False
    max_num = 1
    extra = 0


class LocationAdmin(admin.ModelAdmin):
    exclude = ("point",)
    inlines = [OfficeInline]
    list_display = ("id", "__str__", "type")
    list_display_links = ("__str__",)
    list_filter = (LocationTypeFilter,)
    search_fields = ("address", "city", "postcode")

    def get_search_results(self, request, queryset, term):
        queryset, use_distinct = super(LocationAdmin, self).get_search_results(request, queryset, term)
        office_name_q = Q(office__organisation__name__icontains=term)
        outreach_name_q = Q(outreachservice__office__organisation__name__icontains=term)
        queryset |= self.model.objects.filter(office_name_q | outreach_name_q)
        return queryset, use_distinct


class MyAdminSite(admin.AdminSite):
    def get_urls(self):
        urls = super(MyAdminSite, self).get_urls()
        my_urls = [
            re_path(r"^upload/$", views.upload_spreadsheet),
            re_path(
                r"^import-in-progress/$",
                TemplateView.as_view(
                    template_name="import_progress.html", get_context_data=lambda: {"title": "Importing data"}
                ),
                name="import_in_progress",
            ),
            re_path(r"^import-progress/$", views.import_progress),
        ]
        return my_urls + urls


admin_site = MyAdminSite()
admin_site.index_template = "admin_index.html"
