from django.contrib.gis import admin

from .models import GeographicArea


@admin.register(GeographicArea)
class GeographicAreaAdmin(admin.GISModelAdmin):
    list_display = [
        "name",
        "country_code",
        "admin_level",
        "parent",
        "is_active",
        "created_at",
    ]
    list_filter = ["country_code", "admin_level", "is_active"]
    search_fields = ["name", "country_code"]
    readonly_fields = ["id", "created_at", "updated_at"]
    raw_id_fields = ["parent"]
    ordering = ["country_code", "admin_level", "name"]
