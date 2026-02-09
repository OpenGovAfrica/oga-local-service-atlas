from django.contrib.gis import admin

from .models import Evidence, Report, Verification


class EvidenceInline(admin.TabularInline):
    model = Evidence
    extra = 0
    readonly_fields = ["file_hash", "file_size_bytes", "uploaded_at"]


class VerificationInline(admin.TabularInline):
    model = Verification
    extra = 0
    readonly_fields = ["verified_at"]


@admin.register(Report)
class ReportAdmin(admin.GISModelAdmin):
    list_display = [
        "id",
        "infrastructure_type",
        "reported_status",
        "current_state",
        "reporter_type",
        "is_anonymous",
        "reported_at",
    ]
    list_filter = [
        "current_state",
        "infrastructure_type",
        "reported_status",
        "reporter_type",
        "is_anonymous",
    ]
    search_fields = ["description", "id"]
    readonly_fields = ["id", "reported_at", "last_activity_at"]
    raw_id_fields = ["infrastructure_asset", "reporter"]
    inlines = [EvidenceInline, VerificationInline]
    ordering = ["-reported_at"]


@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "report",
        "evidence_type",
        "source_device",
        "uploaded_at",
    ]
    list_filter = ["evidence_type", "source_device"]
    readonly_fields = ["id", "file_hash", "file_size_bytes", "uploaded_at"]
    raw_id_fields = ["report"]


@admin.register(Verification)
class VerificationAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "report",
        "verified_by",
        "verification_method",
        "is_confirmed",
        "verified_at",
    ]
    list_filter = ["verification_method", "is_confirmed"]
    readonly_fields = ["id", "verified_at"]
    raw_id_fields = ["report", "verified_by"]
