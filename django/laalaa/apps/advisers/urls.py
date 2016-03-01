from django.conf.urls import patterns, url, include

from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register(r'legal-advisers', views.AdviserViewSet, base_name='legal-advisers')

urlpatterns = patterns('',
    url(r'^', include(router.urls))
)
