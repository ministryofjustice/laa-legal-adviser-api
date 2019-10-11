from django.conf.urls import url, include

from rest_framework import routers

from . import views
from categories.views import CategoryViewSet


router = routers.DefaultRouter()
router.register(r"legal-advisers", views.AdviserViewSet, base_name="legal-advisers")
router.register(r"categories", CategoryViewSet, base_name="categories")

urlpatterns = [url(r"^", include(router.urls))]
