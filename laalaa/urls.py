from django.conf.urls import patterns, include, url

from advisers.admin import admin_site


urlpatterns = patterns('',
    url(r'^admin/', include(admin_site.urls)),
    url(r'^', include('advisers.urls')),
)
