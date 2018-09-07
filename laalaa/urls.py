from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.views.decorators.cache import never_cache

from advisers.admin import admin_site
from moj_irat.views import HealthcheckView

urlpatterns = [
    url(r'^healthcheck.json$', never_cache(HealthcheckView.as_view()), name='healthcheck_json'),
    url(r'^admin/', include(admin_site.urls)),
    url(r'^', include('advisers.urls'))
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
