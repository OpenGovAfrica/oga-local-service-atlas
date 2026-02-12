from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from .models import InfrastructureAsset


class InfrastructureAssetSerializer(serializers.ModelSerializer):
    """Standard serializer for InfrastructureAsset."""

    geographic_area_name = serializers.CharField(
        source="geographic_area.name", read_only=True
    )
    asset_type_display = serializers.CharField(
        source="get_asset_type_display", read_only=True
    )
    condition_display = serializers.CharField(
        source="get_condition_display", read_only=True
    )

    class Meta:
        model = InfrastructureAsset
        fields = [
            "id",
            "asset_type",
            "asset_type_display",
            "official_name",
            "local_name",
            "description",
            "location",
            "geographic_area",
            "geographic_area_name",
            "condition",
            "condition_display",
            "condition_verified_at",
            "official_id",
            "is_verified",
            "is_active",
            "data_source",
            "source_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class InfrastructureAssetGeoSerializer(GeoFeatureModelSerializer):
    """GeoJSON serializer for map rendering."""

    asset_type_display = serializers.CharField(
        source="get_asset_type_display", read_only=True
    )
    condition_display = serializers.CharField(
        source="get_condition_display", read_only=True
    )
    geographic_area_name = serializers.CharField(
        source="geographic_area.name", read_only=True
    )

    class Meta:
        model = InfrastructureAsset
        geo_field = "location"
        fields = [
            "id",
            "asset_type",
            "asset_type_display",
            "official_name",
            "local_name",
            "condition",
            "condition_display",
            "geographic_area_name",
            "is_verified",
        ]


class InfrastructureAssetListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for lists."""

    geographic_area_name = serializers.CharField(
        source="geographic_area.name", read_only=True
    )

    class Meta:
        model = InfrastructureAsset
        fields = [
            "id",
            "asset_type",
            "official_name",
            "local_name",
            "condition",
            "geographic_area_name",
        ]
