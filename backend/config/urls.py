"""
URL configuration for OGA Local Service Atlas.
"""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    # API v1
    path("api/v1/", include("apps.core.urls")),
    path("api/v1/geography/", include("apps.geography.urls")),
    path("api/v1/infrastructure/", include("apps.infrastructure.urls")),
    path("api/v1/reports/", include("apps.reports.urls")),
    # Authentication
    path("api/v1/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/v1/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # OpenAPI Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]
