from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from .models import GeographicArea


class GeographicAreaSerializer(serializers.ModelSerializer):
    """Standard serializer for GeographicArea."""

    full_path = serializers.ReadOnlyField()
    parent_name = serializers.CharField(source="parent.name", read_only=True)

    class Meta:
        model = GeographicArea
        fields = [
            "id",
            "name",
            "country_code",
            "admin_level",
            "parent",
            "parent_name",
            "full_path",
            "population",
            "is_active",
            "data_source",
            "source_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class GeographicAreaGeoSerializer(GeoFeatureModelSerializer):
    """GeoJSON serializer for map rendering."""

    full_path = serializers.ReadOnlyField()

    class Meta:
        model = GeographicArea
        geo_field = "geometry"
        fields = [
            "id",
            "name",
            "country_code",
            "admin_level",
            "full_path",
            "population",
            "is_active",
        ]


class GeographicAreaListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for dropdowns and lists."""

    class Meta:
        model = GeographicArea
        fields = ["id", "name", "country_code", "admin_level"]
