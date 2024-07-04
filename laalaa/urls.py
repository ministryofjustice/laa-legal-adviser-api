from django.conf import settings
from django.urls import include, re_path
from django.conf.urls.static import static
from django.views.decorators.cache import never_cache

from advisers.admin import admin_site
from moj_irat.views import HealthcheckView

urlpatterns = [
    re_path(r"^healthcheck.json$", never_cache(HealthcheckView.as_view()), name="healthcheck_json"),
    re_path(r"^admin/", admin_site.urls),
    re_path(r"^", include("advisers.urls")),
    re_path("", include("django_prometheus.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
