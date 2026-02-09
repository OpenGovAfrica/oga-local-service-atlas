from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from .models import Evidence, Report, Verification


class EvidenceSerializer(serializers.ModelSerializer):
    """Serializer for Evidence."""

    evidence_type_display = serializers.CharField(
        source="get_evidence_type_display", read_only=True
    )

    class Meta:
        model = Evidence
        fields = [
            "id",
            "report",
            "evidence_type",
            "evidence_type_display",
            "file",
            "url",
            "file_hash",
            "file_size_bytes",
            "captured_at",
            "uploaded_at",
            "source_device",
            "description",
        ]
        read_only_fields = ["id", "file_hash", "file_size_bytes", "uploaded_at"]


class VerificationSerializer(serializers.ModelSerializer):
    """Serializer for Verification."""

    verified_by_name = serializers.CharField(
        source="verified_by.username", read_only=True
    )

    class Meta:
        model = Verification
        fields = [
            "id",
            "report",
            "verified_by",
            "verified_by_name",
            "verification_method",
            "verified_at",
            "verification_notes",
            "is_confirmed",
        ]
        read_only_fields = ["id", "verified_at"]


class ReportSerializer(serializers.ModelSerializer):
    """Full serializer for Report with nested evidence."""

    evidence = EvidenceSerializer(many=True, read_only=True)
    verifications = VerificationSerializer(many=True, read_only=True)
    infrastructure_type_display = serializers.CharField(
        source="get_infrastructure_type_display", read_only=True
    )
    reported_status_display = serializers.CharField(
        source="get_reported_status_display", read_only=True
    )
    current_state_display = serializers.CharField(
        source="get_current_state_display", read_only=True
    )
    reporter_type_display = serializers.CharField(
        source="get_reporter_type_display", read_only=True
    )

    class Meta:
        model = Report
        fields = [
            "id",
            "infrastructure_asset",
            "infrastructure_type",
            "infrastructure_type_display",
            "reported_status",
            "reported_status_display",
            "description",
            "location",
            "location_accuracy_meters",
            "reporter_type",
            "reporter_type_display",
            "reporter",
            "is_anonymous",
            "current_state",
            "current_state_display",
            "reported_at",
            "last_activity_at",
            "rejection_reason",
            "evidence",
            "verifications",
        ]
        read_only_fields = [
            "id",
            "current_state",
            "reported_at",
            "last_activity_at",
            "rejection_reason",
        ]


class ReportCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new reports."""

    class Meta:
        model = Report
        fields = [
            "infrastructure_asset",
            "infrastructure_type",
            "reported_status",
            "description",
            "location",
            "location_accuracy_meters",
            "reporter_type",
            "is_anonymous",
        ]


class ReportGeoSerializer(GeoFeatureModelSerializer):
    """GeoJSON serializer for map rendering."""

    infrastructure_type_display = serializers.CharField(
        source="get_infrastructure_type_display", read_only=True
    )
    reported_status_display = serializers.CharField(
        source="get_reported_status_display", read_only=True
    )
    current_state_display = serializers.CharField(
        source="get_current_state_display", read_only=True
    )

    class Meta:
        model = Report
        geo_field = "location"
        fields = [
            "id",
            "infrastructure_type",
            "infrastructure_type_display",
            "reported_status",
            "reported_status_display",
            "current_state",
            "current_state_display",
            "reported_at",
        ]


class ReportListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for lists."""

    infrastructure_type_display = serializers.CharField(
        source="get_infrastructure_type_display", read_only=True
    )
    reported_status_display = serializers.CharField(
        source="get_reported_status_display", read_only=True
    )

    class Meta:
        model = Report
        fields = [
            "id",
            "infrastructure_type",
            "infrastructure_type_display",
            "reported_status",
            "reported_status_display",
            "current_state",
            "reported_at",
        ]


class ReportStateTransitionSerializer(serializers.Serializer):
    """Serializer for state transitions."""

    new_state = serializers.ChoiceField(
        choices=[
            ("under_review", "Under Review"),
            ("verified", "Verified"),
            ("rejected", "Rejected"),
            ("resolved", "Resolved"),
        ]
    )
    reason = serializers.CharField(required=False, allow_blank=True)
