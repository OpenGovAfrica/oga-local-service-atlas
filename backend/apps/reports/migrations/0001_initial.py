from django.db import migrations, models
import django.contrib.gis.db.models.fields
from django.conf import settings


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("infrastructure", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Report",
            fields=[
                ("id", models.UUIDField(primary_key=True, editable=False, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "infrastructure_asset",
                    models.ForeignKey(
                        to="infrastructure.infrastructureasset",
                        on_delete=models.SET_NULL,
                        null=True,
                        blank=True,
                        related_name="reports",
                        help_text="Linked infrastructure asset (if known)",
                    ),
                ),
                (
                    "infrastructure_type",
                    models.CharField(
                        max_length=30,
                        choices=[
                            ("school", "School"),
                            ("clinic", "Health Clinic"),
                            ("hospital", "Hospital"),
                            ("water_point", "Water Point"),
                            ("borehole", "Borehole"),
                            ("road", "Road"),
                            ("bridge", "Bridge"),
                            ("sanitation", "Sanitation Facility"),
                            ("electricity", "Electricity Infrastructure"),
                            ("market", "Market"),
                            ("government_office", "Government Office"),
                            ("other", "Other"),
                        ],
                        db_index=True,
                        help_text="Type of infrastructure being reported",
                    ),
                ),
                (
                    "reported_status",
                    models.CharField(
                        max_length=30,
                        choices=[
                            ("working", "Working"),
                            ("partially_working", "Partially Working"),
                            ("broken", "Broken"),
                            ("inaccessible", "Inaccessible"),
                            ("unknown", "Unknown"),
                        ],
                        help_text="Reported status of the infrastructure",
                    ),
                ),
                ("description", models.TextField(help_text="Detailed description of the issue or observation")),
                ("location", django.contrib.gis.db.models.fields.PointField(srid=4326, help_text="Geographic point of the reported issue (GeoJSON)")),
                ("location_accuracy_meters", models.PositiveIntegerField(null=True, blank=True, help_text="GPS accuracy in meters (if available)")),
                (
                    "reporter_type",
                    models.CharField(
                        max_length=30,
                        choices=[
                            ("citizen", "Citizen"),
                            ("government_official", "Government Official"),
                            ("ngo", "NGO Representative"),
                        ],
                        default="citizen",
                        help_text="Type of reporter",
                    ),
                ),
                (
                    "reporter",
                    models.ForeignKey(
                        to=settings.AUTH_USER_MODEL,
                        on_delete=models.SET_NULL,
                        null=True,
                        blank=True,
                        related_name="reports",
                        help_text="User who submitted the report (if not anonymous)",
                    ),
                ),
                ("is_anonymous", models.BooleanField(default=False, help_text="Whether the report was submitted anonymously")),
                (
                    "current_state",
                    models.CharField(
                        max_length=20,
                        choices=[
                            ("submitted", "Submitted"),
                            ("under_review", "Under Review"),
                            ("verified", "Verified"),
                            ("rejected", "Rejected"),
                            ("resolved", "Resolved"),
                        ],
                        default="submitted",
                        db_index=True,
                        help_text="Current workflow state",
                    ),
                ),
                ("reported_at", models.DateTimeField(auto_now_add=True, help_text="When the report was submitted")),
                ("last_activity_at", models.DateTimeField(auto_now=True, help_text="When the report was last updated")),
                ("rejection_reason", models.TextField(blank=True, help_text="Reason for rejection (if rejected)")),
            ],
            options={
                "verbose_name": "Report",
                "verbose_name_plural": "Reports",
                "ordering": ["-reported_at"],
            },
        ),
        migrations.AddIndex(
            model_name="report",
            index=models.Index(fields=["current_state", "reported_at"], name="report_state_time_idx"),
        ),
        migrations.AddIndex(
            model_name="report",
            index=models.Index(fields=["infrastructure_type"], name="report_infra_type_idx"),
        ),
        migrations.AddIndex(
            model_name="report",
            index=models.Index(fields=["reported_status"], name="report_status_idx"),
        ),
        migrations.CreateModel(
            name="Evidence",
            fields=[
                ("id", models.UUIDField(primary_key=True, editable=False, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "report",
                    models.ForeignKey(
                        to="reports.report",
                        on_delete=models.CASCADE,
                        related_name="evidence",
                        help_text="Report this evidence belongs to",
                    ),
                ),
                (
                    "evidence_type",
                    models.CharField(
                        max_length=20,
                        choices=[
                            ("photo", "Photo"),
                            ("video", "Video"),
                            ("document", "Document"),
                            ("audio", "Audio Recording"),
                            ("link", "External Link"),
                        ],
                        help_text="Type of evidence",
                    ),
                ),
                ("file", models.FileField(upload_to="evidence/%Y/%m/%d/", null=True, blank=True, help_text="Uploaded evidence file")),
                ("url", models.URLField(null=True, blank=True, help_text="External URL (for link-type evidence)")),
                ("file_hash", models.CharField(max_length=64, blank=True, help_text="SHA-256 hash of the file for integrity verification")),
                ("file_size_bytes", models.PositiveIntegerField(null=True, blank=True, help_text="File size in bytes")),
                ("captured_at", models.DateTimeField(null=True, blank=True, help_text="When the evidence was captured (from EXIF or user input)")),
                ("uploaded_at", models.DateTimeField(auto_now_add=True, help_text="When the evidence was uploaded")),
                (
                    "source_device",
                    models.CharField(
                        max_length=50,
                        blank=True,
                        choices=[
                            ("camera", "Camera/Phone"),
                            ("upload", "File Upload"),
                            ("screenshot", "Screenshot"),
                            ("other", "Other"),
                        ],
                        help_text="Device/method used to capture evidence",
                    ),
                ),
                ("description", models.TextField(blank=True, help_text="Description of the evidence")),
            ],
            options={
                "verbose_name": "Evidence",
                "verbose_name_plural": "Evidence",
                "ordering": ["-uploaded_at"],
            },
        ),
        migrations.CreateModel(
            name="Verification",
            fields=[
                ("id", models.UUIDField(primary_key=True, editable=False, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "report",
                    models.ForeignKey(
                        to="reports.report",
                        on_delete=models.CASCADE,
                        related_name="verifications",
                        help_text="Report being verified",
                    ),
                ),
                (
                    "verified_by",
                    models.ForeignKey(
                        to=settings.AUTH_USER_MODEL,
                        on_delete=models.SET_NULL,
                        null=True,
                        related_name="verifications_made",
                        help_text="User who performed verification",
                    ),
                ),
                (
                    "verification_method",
                    models.CharField(
                        max_length=30,
                        choices=[
                            ("site_visit", "Site Visit"),
                            ("document", "Document Review"),
                            ("photo", "Photo Verification"),
                            ("cross_reference", "Cross-Reference with Official Data"),
                            ("other", "Other"),
                        ],
                        help_text="Method used for verification",
                    ),
                ),
                ("verified_at", models.DateTimeField(auto_now_add=True, help_text="When verification was performed")),
                ("verification_notes", models.TextField(blank=True, help_text="Notes from the verification process")),
                ("is_confirmed", models.BooleanField(help_text="Whether the report was confirmed as accurate")),
            ],
            options={
                "verbose_name": "Verification",
                "verbose_name_plural": "Verifications",
                "ordering": ["-verified_at"],
            },
        ),
    ]
