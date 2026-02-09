from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import GeographicArea
from .serializers import (
    GeographicAreaGeoSerializer,
    GeographicAreaListSerializer,
    GeographicAreaSerializer,
)


class GeographicAreaFilter(filters.FilterSet):
    """Filter for GeographicArea queries."""

    country = filters.CharFilter(field_name="country_code", lookup_expr="iexact")
    level = filters.CharFilter(field_name="admin_level", lookup_expr="iexact")
    parent_id = filters.UUIDFilter(field_name="parent__id")

    class Meta:
        model = GeographicArea
        fields = ["country_code", "admin_level", "parent", "is_active"]


class GeographicAreaViewSet(viewsets.ModelViewSet):
    """
    API endpoints for Geographic Areas.

    Supports filtering by country_code, admin_level, and parent.
    Provides GeoJSON output for map rendering.
    """

    queryset = GeographicArea.objects.filter(is_active=True).select_related("parent")
    serializer_class = GeographicAreaSerializer
    filterset_class = GeographicAreaFilter
    search_fields = ["name"]
    ordering_fields = ["name", "admin_level", "created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return GeographicAreaListSerializer
        if self.action == "geojson":
            return GeographicAreaGeoSerializer
        return GeographicAreaSerializer

    @action(detail=False, methods=["get"])
    def geojson(self, request):
        """Return all areas as GeoJSON FeatureCollection."""
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.exclude(geometry__isnull=True)
        serializer = GeographicAreaGeoSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def children(self, request, pk=None):
        """Return direct children of this area."""
        area = self.get_object()
        children = area.children.filter(is_active=True)
        serializer = GeographicAreaListSerializer(children, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def countries(self, request):
        """Return list of available countries."""
        countries = (
            GeographicArea.objects.filter(admin_level="country", is_active=True)
            .values("id", "name", "country_code")
            .distinct()
        )
        return Response(list(countries))
