"""
Report and Evidence models for OGA Local Service Atlas.

Phase 1.4: Report Data Model
Phase 1.5: Evidence & Provenance Model
Phase 1.6: Reporting Workflow State Machine
"""

import hashlib

from django.conf import settings
from django.contrib.gis.db import models as gis_models
from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import BaseModel
from apps.infrastructure.models import AssetType, InfrastructureAsset


class ReportedStatus(models.TextChoices):
    """
    Status reported by citizens/officials about infrastructure.
    """

    WORKING = "working", "Working"
    PARTIALLY_WORKING = "partially_working", "Partially Working"
    BROKEN = "broken", "Broken"
    INACCESSIBLE = "inaccessible", "Inaccessible"
    UNKNOWN = "unknown", "Unknown"


class ReporterType(models.TextChoices):
    """
    Type of entity submitting the report.
    """

    CITIZEN = "citizen", "Citizen"
    GOVERNMENT_OFFICIAL = "government_official", "Government Official"
    NGO = "ngo", "NGO Representative"


class ReportState(models.TextChoices):
    """
    Workflow states for reports.

    Phase 1.6: Valid transitions:
    - Submitted → Under-Review
    - Under-Review → Verified
    - Under-Review → Rejected
    - Verified → Resolved
    """

    SUBMITTED = "submitted", "Submitted"
    UNDER_REVIEW = "under_review", "Under Review"
    VERIFIED = "verified", "Verified"
    REJECTED = "rejected", "Rejected"
    RESOLVED = "resolved", "Resolved"


# Valid state transitions (Phase 1.6)
VALID_STATE_TRANSITIONS = {
    ReportState.SUBMITTED: [ReportState.UNDER_REVIEW],
    ReportState.UNDER_REVIEW: [ReportState.VERIFIED, ReportState.REJECTED],
    ReportState.VERIFIED: [ReportState.RESOLVED],
    ReportState.REJECTED: [],
    ReportState.RESOLVED: [],
}


class Report(BaseModel):
    """
    Citizen/Official report about infrastructure status.

    Phase 1.4 fields:
    - report_id (inherited as 'id')
    - infrastructure_asset_id (nullable FK)
    - infrastructure_type
    - reported_status
    - description
    - geographic_point (GeoJSON)
    - location_accuracy_meters (nullable)
    - reporter_type
    - is_anonymous
    - current_state
    - reported_at
    - last_activity_at
    """

    # Link to existing asset (nullable for new/unknown assets)
    infrastructure_asset = models.ForeignKey(
        InfrastructureAsset,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reports",
        help_text="Linked infrastructure asset (if known)",
    )

    # Infrastructure type (required even if asset not linked)
    infrastructure_type = models.CharField(
        max_length=30,
        choices=AssetType.choices,
        db_index=True,
        help_text="Type of infrastructure being reported",
    )

    # Report content
    reported_status = models.CharField(
        max_length=30,
        choices=ReportedStatus.choices,
        help_text="Reported status of the infrastructure",
    )
    description = models.TextField(
        help_text="Detailed description of the issue or observation",
    )

    # Geospatial location
    location = gis_models.PointField(
        srid=4326,
        help_text="Geographic point of the reported issue (GeoJSON)",
    )
    location_accuracy_meters = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="GPS accuracy in meters (if available)",
    )

    # Reporter information
    reporter_type = models.CharField(
        max_length=30,
        choices=ReporterType.choices,
        default=ReporterType.CITIZEN,
        help_text="Type of reporter",
    )
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reports",
        help_text="User who submitted the report (if not anonymous)",
    )
    is_anonymous = models.BooleanField(
        default=False,
        help_text="Whether the report was submitted anonymously",
    )

    # Workflow state (Phase 1.6)
    current_state = models.CharField(
        max_length=20,
        choices=ReportState.choices,
        default=ReportState.SUBMITTED,
        db_index=True,
        help_text="Current workflow state",
    )

    # Timestamps
    reported_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the report was submitted",
    )
    last_activity_at = models.DateTimeField(
        auto_now=True,
        help_text="When the report was last updated",
    )

    # Moderation
    rejection_reason = models.TextField(
        blank=True,
        help_text="Reason for rejection (if rejected)",
    )

    class Meta:
        verbose_name = "Report"
        verbose_name_plural = "Reports"
        ordering = ["-reported_at"]
        indexes = [
            models.Index(fields=["current_state", "reported_at"]),
            models.Index(fields=["infrastructure_type"]),
            models.Index(fields=["reported_status"]),
        ]

    def __str__(self):
        return f"Report #{str(self.id)[:8]} - {self.get_reported_status_display()}"

    def can_transition_to(self, new_state: str) -> bool:
        """Check if transition to new_state is valid."""
        valid_transitions = VALID_STATE_TRANSITIONS.get(self.current_state, [])
        return new_state in valid_transitions

    def transition_to(self, new_state: str) -> None:
        """
        Transition report to a new state.
        Raises ValidationError if transition is invalid.
        """
        if not self.can_transition_to(new_state):
            raise ValidationError(
                f"Invalid state transition from {self.current_state} to {new_state}. "
                f"Valid transitions: {VALID_STATE_TRANSITIONS.get(self.current_state, [])}"
            )
        self.current_state = new_state
        self.save(update_fields=["current_state", "last_activity_at"])


class EvidenceType(models.TextChoices):
    """Types of evidence that can be attached to reports."""

    PHOTO = "photo", "Photo"
    VIDEO = "video", "Video"
    DOCUMENT = "document", "Document"
    AUDIO = "audio", "Audio Recording"
    LINK = "link", "External Link"


class Evidence(BaseModel):
    """
    Evidence attached to reports.

    Phase 1.5: Every report must include at least one piece of evidence,
    unless explicitly flagged as low-confidence.

    Fields:
    - evidence_id (inherited as 'id')
    - report_id (FK)
    - evidence_type
    - file_path or URL
    - file_hash
    - captured_at
    - uploaded_at
    - source_device
    """

    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name="evidence",
        help_text="Report this evidence belongs to",
    )

    evidence_type = models.CharField(
        max_length=20,
        choices=EvidenceType.choices,
        help_text="Type of evidence",
    )

    # File or URL (one must be provided)
    file = models.FileField(
        upload_to="evidence/%Y/%m/%d/",
        null=True,
        blank=True,
        help_text="Uploaded evidence file",
    )
    url = models.URLField(
        null=True,
        blank=True,
        help_text="External URL (for link-type evidence)",
    )

    # Integrity and provenance
    file_hash = models.CharField(
        max_length=64,
        blank=True,
        help_text="SHA-256 hash of the file for integrity verification",
    )
    file_size_bytes = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="File size in bytes",
    )

    # Timestamps
    captured_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the evidence was captured (from EXIF or user input)",
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the evidence was uploaded",
    )

    # Source metadata
    source_device = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ("camera", "Camera/Phone"),
            ("upload", "File Upload"),
            ("screenshot", "Screenshot"),
            ("other", "Other"),
        ],
        help_text="Device/method used to capture evidence",
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the evidence",
    )

    class Meta:
        verbose_name = "Evidence"
        verbose_name_plural = "Evidence"
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.get_evidence_type_display()} for Report #{str(self.report_id)[:8]}"

    def clean(self):
        """Validate that either file or URL is provided."""
        if not self.file and not self.url:
            raise ValidationError("Either file or URL must be provided.")
        if self.file and self.url:
            raise ValidationError("Provide either file or URL, not both.")

    def save(self, *args, **kwargs):
        """Calculate file hash on save if file is provided."""
        if self.file and not self.file_hash:
            self.file_hash = self._calculate_file_hash()
            self.file_size_bytes = self.file.size
        super().save(*args, **kwargs)

    def _calculate_file_hash(self) -> str:
        """Calculate SHA-256 hash of the file."""
        sha256 = hashlib.sha256()
        for chunk in self.file.chunks():
            sha256.update(chunk)
        return sha256.hexdigest()


class Verification(BaseModel):
    """
    Verification action on a report.

    Phase 4.1 preparation: Track verification actions with full audit trail.
    """

    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name="verifications",
        help_text="Report being verified",
    )
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="verifications_made",
        help_text="User who performed verification",
    )
    verification_method = models.CharField(
        max_length=30,
        choices=[
            ("site_visit", "Site Visit"),
            ("document", "Document Review"),
            ("photo", "Photo Verification"),
            ("cross_reference", "Cross-Reference with Official Data"),
            ("other", "Other"),
        ],
        help_text="Method used for verification",
    )
    verified_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When verification was performed",
    )
    verification_notes = models.TextField(
        blank=True,
        help_text="Notes from the verification process",
    )
    is_confirmed = models.BooleanField(
        help_text="Whether the report was confirmed as accurate",
    )

    class Meta:
        verbose_name = "Verification"
        verbose_name_plural = "Verifications"
        ordering = ["-verified_at"]

    def __str__(self):
        status = "Confirmed" if self.is_confirmed else "Not Confirmed"
        return f"Verification ({status}) for Report #{str(self.report_id)[:8]}"
