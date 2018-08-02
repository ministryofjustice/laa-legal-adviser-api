from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static

from advisers.admin import admin_site
import healthcheck.views

urlpatterns = [
    url(r'^ping.json$', healthcheck.views.ping),
    url(r'^healthcheck.json$', healthcheck.views.healthcheck),
    url(r'^admin/', include(admin_site.urls)),
    url(r'^', include('advisers.urls'))
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
