from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static

from advisers.admin import admin_site


urlpatterns = patterns('',
    url(r'^admin/', include(admin_site.urls)),
    url(r'^', include('advisers.urls')),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
