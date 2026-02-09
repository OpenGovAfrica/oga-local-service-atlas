"""
Core models and abstract base classes for OGA Local Service Atlas.

All models inherit from these base classes to ensure consistent
audit trails and timestamps across the platform.
"""

import uuid

from django.db import models


class TimestampedModel(models.Model):
    """
    Abstract base model that provides self-updating
    created_at and updated_at fields.
    """

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDModel(models.Model):
    """
    Abstract base model that uses UUID as primary key.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class BaseModel(UUIDModel, TimestampedModel):
    """
    Abstract base model combining UUID primary key and timestamps.
    All domain models should inherit from this.
    """

    class Meta:
        abstract = True


class DataSourceType(models.TextChoices):
    """
    Enumeration of valid data source types.
    Tracks provenance of data entries.
    """

    OFFICIAL = "official", "Official Government Source"
    NGO = "ngo", "NGO / Civil Society"
    COMMUNITY = "community", "Community Reported"
    RESEARCH = "research", "Research / Academic"


class AuditableModel(BaseModel):
    """
    Abstract model for entities that require full audit trail.
    Tracks data source and provenance information.
    """

    data_source = models.CharField(
        max_length=20,
        choices=DataSourceType.choices,
        default=DataSourceType.COMMUNITY,
        help_text="Origin of this data entry",
    )
    source_url = models.URLField(
        blank=True,
        null=True,
        help_text="URL reference to the source of this data",
    )
    source_notes = models.TextField(
        blank=True,
        help_text="Additional notes about data provenance",
    )

    class Meta:
        abstract = True
