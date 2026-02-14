from django.core.exceptions import ValidationError
from django_filters import rest_framework as filters
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Evidence, Report, ReportState, Verification
from .serializers import (
    EvidenceSerializer,
    ReportCreateSerializer,
    ReportGeoSerializer,
    ReportListSerializer,
    ReportSerializer,
    ReportStateTransitionSerializer,
    VerificationSerializer,
)


class ReportFilter(filters.FilterSet):
    """Filter for Report queries."""

    infrastructure_type = filters.CharFilter(lookup_expr="iexact")
    reported_status = filters.CharFilter(lookup_expr="iexact")
    state = filters.CharFilter(field_name="current_state", lookup_expr="iexact")
    reporter_type = filters.CharFilter(lookup_expr="iexact")
    asset = filters.UUIDFilter(field_name="infrastructure_asset__id")
    since = filters.DateTimeFilter(field_name="reported_at", lookup_expr="gte")
    until = filters.DateTimeFilter(field_name="reported_at", lookup_expr="lte")

    class Meta:
        model = Report
        fields = [
            "infrastructure_type",
            "reported_status",
            "current_state",
            "reporter_type",
            "is_anonymous",
        ]


class ReportViewSet(viewsets.ModelViewSet):
    """
    API endpoints for Reports.

    Supports filtering by infrastructure_type, reported_status, current_state.
    Provides GeoJSON output for map rendering.
    Includes state transition endpoints for workflow management.
    """

    queryset = (
        Report.objects.all().select_related("infrastructure_asset").prefetch_related("evidence")
    )
    serializer_class = ReportSerializer
    filterset_class = ReportFilter
    search_fields = ["description"]
    ordering_fields = ["reported_at", "last_activity_at", "current_state"]

    def get_serializer_class(self):
        if self.action == "list":
            return ReportListSerializer
        if self.action == "create":
            return ReportCreateSerializer
        if self.action == "geojson":
            return ReportGeoSerializer
        if self.action == "transition":
            return ReportStateTransitionSerializer
        return ReportSerializer

    def perform_create(self, serializer):
        """Set reporter if user is authenticated and not anonymous."""
        report = serializer.save()
        if self.request.user.is_authenticated and not report.is_anonymous:
            report.reporter = self.request.user
            report.save(update_fields=["reporter"])

    @action(detail=False, methods=["get"])
    def geojson(self, request):
        """Return all reports as GeoJSON FeatureCollection."""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = ReportGeoSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def transition(self, request, pk=None):
        """
        Transition report to a new state.

        Phase 1.6: Enforces valid state transitions.
        """
        report = self.get_object()
        serializer = ReportStateTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_state = serializer.validated_data["new_state"]
        reason = serializer.validated_data.get("reason", "")

        try:
            # Store rejection reason if rejecting
            if new_state == ReportState.REJECTED and reason:
                report.rejection_reason = reason

            report.transition_to(new_state)
            return Response(
                {
                    "status": "success",
                    "message": f"Report transitioned to {new_state}",
                    "current_state": report.current_state,
                }
            )
        except ValidationError as e:
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """Return summary statistics for reports."""
        queryset = self.filter_queryset(self.get_queryset())
        stats = {
            "total": queryset.count(),
            "by_state": {},
            "by_status": {},
            "by_type": {},
        }

        for state in ReportState.values:
            count = queryset.filter(current_state=state).count()
            if count > 0:
                stats["by_state"][state] = count

        for status_val in queryset.values_list("reported_status", flat=True).distinct():
            stats["by_status"][status_val] = queryset.filter(reported_status=status_val).count()

        for type_val in queryset.values_list("infrastructure_type", flat=True).distinct():
            stats["by_type"][type_val] = queryset.filter(infrastructure_type=type_val).count()

        return Response(stats)

    @action(detail=False, methods=["get"])
    def pending_review(self, request):
        """Return reports pending review."""
        queryset = self.get_queryset().filter(current_state=ReportState.SUBMITTED)
        serializer = ReportListSerializer(queryset, many=True)
        return Response(serializer.data)


class EvidenceViewSet(viewsets.ModelViewSet):
    """API endpoints for Evidence."""

    queryset = Evidence.objects.all()
    serializer_class = EvidenceSerializer
    filterset_fields = ["report", "evidence_type", "source_device"]


class VerificationViewSet(viewsets.ModelViewSet):
    """API endpoints for Verification."""

    queryset = Verification.objects.all().select_related("verified_by")
    serializer_class = VerificationSerializer
    filterset_fields = ["report", "verification_method", "is_confirmed"]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Set verified_by to current user."""
        serializer.save(verified_by=self.request.user)
