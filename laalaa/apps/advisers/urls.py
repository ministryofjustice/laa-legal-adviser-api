from django.urls import re_path, include

from rest_framework import routers

from . import views
from categories.views import CategoryViewSet


router = routers.DefaultRouter()
router.register(r"legal-advisers", views.AdviserViewSet, basename="legal-advisers")
router.register(r"categories_of_law", CategoryViewSet, basename="categories")

urlpatterns = [re_path(r"^", include(router.urls))]
