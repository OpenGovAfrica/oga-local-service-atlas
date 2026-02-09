from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import EvidenceViewSet, ReportViewSet, VerificationViewSet

app_name = "reports"

router = DefaultRouter()
router.register(r"", ReportViewSet, basename="report")
router.register(r"evidence", EvidenceViewSet, basename="evidence")
router.register(r"verifications", VerificationViewSet, basename="verification")

urlpatterns = [
    path("", include(router.urls)),
]
