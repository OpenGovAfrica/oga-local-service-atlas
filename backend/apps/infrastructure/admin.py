from django.contrib.gis import admin

from .models import InfrastructureAsset


@admin.register(InfrastructureAsset)
class InfrastructureAssetAdmin(admin.GISModelAdmin):
    list_display = [
        "official_name",
        "asset_type",
        "geographic_area",
        "condition",
        "is_verified",
        "data_source",
        "created_at",
    ]
    list_filter = ["asset_type", "condition", "is_verified", "data_source"]
    search_fields = ["official_name", "local_name", "official_id"]
    readonly_fields = ["id", "created_at", "updated_at"]
    raw_id_fields = ["geographic_area"]
    ordering = ["-created_at"]
