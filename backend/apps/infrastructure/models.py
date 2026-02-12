"""
Infrastructure Asset models for OGA Local Service Atlas.

Phase 1.2: Infrastructure Asset Model

Represents public infrastructure assets (schools, clinics, water points, etc.)
with geospatial location and provenance tracking.
"""

from django.contrib.gis.db import models as gis_models
from django.db import models

from apps.core.models import AuditableModel
from apps.geography.models import GeographicArea


class AssetType(models.TextChoices):
    """
    Types of public infrastructure assets.
    Extensible for future asset categories.
    """

    SCHOOL = "school", "School"
    CLINIC = "clinic", "Health Clinic"
    HOSPITAL = "hospital", "Hospital"
    WATER_POINT = "water_point", "Water Point"
    BOREHOLE = "borehole", "Borehole"
    ROAD = "road", "Road"
    BRIDGE = "bridge", "Bridge"
    SANITATION = "sanitation", "Sanitation Facility"
    ELECTRICITY = "electricity", "Electricity Infrastructure"
    MARKET = "market", "Market"
    GOVERNMENT_OFFICE = "government_office", "Government Office"
    OTHER = "other", "Other"


class AssetCondition(models.TextChoices):
    """
    Current condition/status of infrastructure assets.
    """

    FUNCTIONAL = "functional", "Functional"
    PARTIALLY_FUNCTIONAL = "partially_functional", "Partially Functional"
    NON_FUNCTIONAL = "non_functional", "Non-Functional"
    UNDER_CONSTRUCTION = "under_construction", "Under Construction"
    ABANDONED = "abandoned", "Abandoned"
    UNKNOWN = "unknown", "Unknown"


class InfrastructureAsset(AuditableModel):
    """
    Infrastructure Asset model.

    Represents a public infrastructure asset with geospatial location.
    Linked to a normalized GeographicArea for spatial queries.

    Phase 1.2 fields:
    - asset_id (inherited as 'id' from UUIDModel)
    - asset_type
    - official_name (nullable)
    - geographic_point (GeoJSON)
    - geographic_area_id (FK)
    - data_source (inherited from AuditableModel)
    - created_at / updated_at (inherited from TimestampedModel)
    """

    asset_type = models.CharField(
        max_length=30,
        choices=AssetType.choices,
        db_index=True,
        help_text="Type of infrastructure asset",
    )
    official_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Official name of the asset (if known)",
    )
    local_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Local or commonly used name",
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the asset",
    )

    # Geospatial location (required)
    location = gis_models.PointField(
        srid=4326,
        help_text="Geographic point location (GeoJSON compatible)",
    )

    # Link to normalized geographic area (required - no free-text locations)
    geographic_area = models.ForeignKey(
        GeographicArea,
        on_delete=models.PROTECT,
        related_name="assets",
        help_text="Geographic area this asset belongs to",
    )

    # Current status
    condition = models.CharField(
        max_length=30,
        choices=AssetCondition.choices,
        default=AssetCondition.UNKNOWN,
        help_text="Current condition of the asset",
    )
    condition_verified_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the condition was last verified",
    )

    # Official identifiers (if available)
    official_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="Official government identifier (if any)",
    )

    # Metadata
    is_verified = models.BooleanField(
        default=False,
        help_text="Whether this asset has been verified",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this asset record is active",
    )

    class Meta:
        verbose_name = "Infrastructure Asset"
        verbose_name_plural = "Infrastructure Assets"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["asset_type", "geographic_area"]),
            models.Index(fields=["condition"]),
            models.Index(fields=["is_verified"]),
        ]

    def __str__(self):
        name = self.official_name or self.local_name or f"{self.get_asset_type_display()}"
        return f"{name} ({self.geographic_area.name})"
