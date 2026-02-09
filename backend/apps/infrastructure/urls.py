from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import InfrastructureAssetViewSet

app_name = "infrastructure"

router = DefaultRouter()
router.register(r"assets", InfrastructureAssetViewSet, basename="infrastructure-asset")

urlpatterns = [
    path("", include(router.urls)),
]
