from django.conf.urls import url, include

from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register(r'legal-advisers', views.AdviserViewSet, base_name='legal-advisers')

urlpatterns = [
    url(r'^', include(router.urls))
]
