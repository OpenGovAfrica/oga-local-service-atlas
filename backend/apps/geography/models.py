"""
Geographic Area models for OGA Local Service Atlas.

Phase 1.3: Geographic Area Model

Design Note: Free-text locations are not allowed.
All assets and reports must link to normalized geographic areas.
"""

from django.contrib.gis.db import models as gis_models
from django.db import models

from apps.core.models import AuditableModel


class AdminLevel(models.TextChoices):
    """
    Administrative levels for geographic hierarchy.
    Supports diverse African governance structures.
    """

    COUNTRY = "country", "Country"
    STATE = "state", "State / Region"
    PROVINCE = "province", "Province"
    DISTRICT = "district", "District"
    COUNTY = "county", "County"
    LGA = "lga", "Local Government Area"
    WARD = "ward", "Ward"
    VILLAGE = "village", "Village / Settlement"


class GeographicArea(AuditableModel):
    """
    Normalized geographic area model.

    Represents administrative divisions at various levels.
    Supports hierarchical relationships (e.g., ward -> district -> state -> country).

    All spatial queries and asset/report locations must reference
    a GeographicArea rather than free-text locations.
    """

    name = models.CharField(
        max_length=255,
        help_text="Official name of the geographic area",
    )
    country_code = models.CharField(
        max_length=3,
        db_index=True,
        help_text="ISO 3166-1 alpha-3 country code (e.g., NGA, KEN, ZAF)",
    )
    admin_level = models.CharField(
        max_length=20,
        choices=AdminLevel.choices,
        db_index=True,
        help_text="Administrative level of this area",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="children",
        help_text="Parent geographic area in hierarchy",
    )

    # Optional geometry for map rendering and spatial queries
    geometry = gis_models.MultiPolygonField(
        srid=4326,  # WGS84 coordinate system
        null=True,
        blank=True,
        help_text="Geographic boundary as MultiPolygon (GeoJSON compatible)",
    )

    # Centroid for quick point-based lookups
    centroid = gis_models.PointField(
        srid=4326,
        null=True,
        blank=True,
        help_text="Center point of the geographic area",
    )

    # Metadata
    population = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Estimated population (for prioritization)",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this area is currently active/valid",
    )

    class Meta:
        verbose_name = "Geographic Area"
        verbose_name_plural = "Geographic Areas"
        ordering = ["country_code", "admin_level", "name"]
        indexes = [
            models.Index(fields=["country_code", "admin_level"]),
            models.Index(fields=["parent"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "country_code", "admin_level", "parent"],
                name="unique_geographic_area",
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.get_admin_level_display()}, {self.country_code})"

    @property
    def full_path(self) -> str:
        """Returns full hierarchical path (e.g., 'Nigeria > Lagos > Ikeja')"""
        parts = [self.name]
        current = self.parent
        while current:
            parts.insert(0, current.name)
            current = current.parent
        return " > ".join(parts)
