from django.db import migrations, models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("geography", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="InfrastructureAsset",
            fields=[
                ("id", models.UUIDField(primary_key=True, editable=False, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "data_source",
                    models.CharField(
                        max_length=20,
                        default="community",
                        choices=[
                            ("official", "Official Government Source"),
                            ("ngo", "NGO / Civil Society"),
                            ("community", "Community Reported"),
                            ("research", "Research / Academic"),
                        ],
                        help_text="Origin of this data entry",
                    ),
                ),
                (
                    "source_url",
                    models.URLField(blank=True, null=True, help_text="URL reference to the source of this data"),
                ),
                ("source_notes", models.TextField(blank=True, help_text="Additional notes about data provenance")),
                (
                    "asset_type",
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
                        help_text="Type of infrastructure asset",
                    ),
                ),
                ("official_name", models.CharField(max_length=255, blank=True, null=True, help_text="Official name of the asset (if known)")),
                ("local_name", models.CharField(max_length=255, blank=True, help_text="Local or commonly used name")),
                ("description", models.TextField(blank=True, help_text="Description of the asset")),
                (
                    "location",
                    django.contrib.gis.db.models.fields.PointField(
                        srid=4326, help_text="Geographic point location (GeoJSON compatible)"
                    ),
                ),
                (
                    "condition",
                    models.CharField(
                        max_length=30,
                        choices=[
                            ("functional", "Functional"),
                            ("partially_functional", "Partially Functional"),
                            ("non_functional", "Non-Functional"),
                            ("under_construction", "Under Construction"),
                            ("abandoned", "Abandoned"),
                            ("unknown", "Unknown"),
                        ],
                        default="unknown",
                        help_text="Current condition of the asset",
                    ),
                ),
                (
                    "condition_verified_at",
                    models.DateTimeField(null=True, blank=True, help_text="When the condition was last verified"),
                ),
                ("official_id", models.CharField(max_length=100, blank=True, help_text="Official government identifier (if any)")),
                ("is_verified", models.BooleanField(default=False, help_text="Whether this asset has been verified")),
                ("is_active", models.BooleanField(default=True, help_text="Whether this asset record is active")),
                (
                    "geographic_area",
                    models.ForeignKey(
                        to="geography.geographicarea",
                        on_delete=models.PROTECT,
                        related_name="assets",
                        help_text="Geographic area this asset belongs to",
                    ),
                ),
            ],
            options={
                "verbose_name": "Infrastructure Asset",
                "verbose_name_plural": "Infrastructure Assets",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="infrastructureasset",
            index=models.Index(fields=["asset_type", "geographic_area"], name="asset_type_area_idx"),
        ),
        migrations.AddIndex(
            model_name="infrastructureasset",
            index=models.Index(fields=["condition"], name="asset_condition_idx"),
        ),
        migrations.AddIndex(
            model_name="infrastructureasset",
            index=models.Index(fields=["is_verified"], name="asset_verified_idx"),
        ),
    ]
