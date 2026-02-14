from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import AssetType, InfrastructureAsset
from .serializers import (
    InfrastructureAssetGeoSerializer,
    InfrastructureAssetListSerializer,
    InfrastructureAssetSerializer,
)


class InfrastructureAssetFilter(filters.FilterSet):
    """Filter for InfrastructureAsset queries."""

    asset_type = filters.CharFilter(lookup_expr="iexact")
    condition = filters.CharFilter(lookup_expr="iexact")
    area = filters.UUIDFilter(field_name="geographic_area__id")
    country = filters.CharFilter(field_name="geographic_area__country_code", lookup_expr="iexact")
    verified = filters.BooleanFilter(field_name="is_verified")

    class Meta:
        model = InfrastructureAsset
        fields = ["asset_type", "condition", "geographic_area", "is_verified", "data_source"]


class InfrastructureAssetViewSet(viewsets.ModelViewSet):
    """
    API endpoints for Infrastructure Assets.

    Supports filtering by asset_type, condition, geographic_area, and verification status.
    Provides GeoJSON output for map rendering.
    """

    queryset = InfrastructureAsset.objects.filter(is_active=True).select_related("geographic_area")
    serializer_class = InfrastructureAssetSerializer
    filterset_class = InfrastructureAssetFilter
    search_fields = ["official_name", "local_name", "description"]
    ordering_fields = ["created_at", "asset_type", "condition"]

    def get_serializer_class(self):
        if self.action == "list":
            return InfrastructureAssetListSerializer
        if self.action == "geojson":
            return InfrastructureAssetGeoSerializer
        return InfrastructureAssetSerializer

    @action(detail=False, methods=["get"])
    def geojson(self, request):
        """Return all assets as GeoJSON FeatureCollection."""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = InfrastructureAssetGeoSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def asset_types(self, request):
        """Return list of available asset types."""
        types = [{"value": choice[0], "label": choice[1]} for choice in AssetType.choices]
        return Response(types)

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """Return summary statistics for assets."""
        queryset = self.filter_queryset(self.get_queryset())
        stats = {
            "total": queryset.count(),
            "verified": queryset.filter(is_verified=True).count(),
            "by_type": {},
            "by_condition": {},
        }

        for asset_type in AssetType.values:
            count = queryset.filter(asset_type=asset_type).count()
            if count > 0:
                stats["by_type"][asset_type] = count

        for condition in queryset.values_list("condition", flat=True).distinct():
            stats["by_condition"][condition] = queryset.filter(condition=condition).count()

        return Response(stats)
