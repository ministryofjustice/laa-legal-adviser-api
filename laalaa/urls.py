from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.views.decorators.cache import never_cache

from advisers.admin import admin_site
from moj_irat.views import PingJsonView, HealthcheckView

urlpatterns = [
    url(r'^ping.json$', never_cache(PingJsonView.as_view(
        build_tag_key='APP_BUILD_TAG',
        build_date_key='APP_BUILD_DATE',
        commit_id_key='APP_GIT_COMMIT',
        version_number_key='APPVERSION',
    )), name='ping_json'),
    url(r'^healthcheck.json$', never_cache(HealthcheckView.as_view()), name='healthcheck_json'),
    url(r'^admin/', include(admin_site.urls)),
    url(r'^', include('advisers.urls'))
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
