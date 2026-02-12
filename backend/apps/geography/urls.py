from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import GeographicAreaViewSet

app_name = "geography"

router = DefaultRouter()
router.register(r"areas", GeographicAreaViewSet, basename="geographic-area")

urlpatterns = [
    path("", include(router.urls)),
]
