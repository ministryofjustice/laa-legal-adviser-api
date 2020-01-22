from django.conf.urls import url, include

from rest_framework import routers

from . import views
from categories.views import CategoryViewSet


router = routers.DefaultRouter()
router.register(r"legal-advisers", views.AdviserViewSet, basename="legal-advisers")
router.register(r"categories_of_law", CategoryViewSet, basename="categories")

urlpatterns = [url(r"^", include(router.urls))]
