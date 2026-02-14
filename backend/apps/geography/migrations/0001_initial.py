from django.db import migrations, models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="GeographicArea",
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
                ("name", models.CharField(max_length=255, help_text="Official name of the geographic area")),
                (
                    "country_code",
                    models.CharField(
                        max_length=3,
                        db_index=True,
                        help_text="ISO 3166-1 alpha-3 country code (e.g., NGA, KEN, ZAF)",
                    ),
                ),
                (
                    "admin_level",
                    models.CharField(
                        max_length=20,
                        db_index=True,
                        choices=[
                            ("country", "Country"),
                            ("state", "State / Region"),
                            ("province", "Province"),
                            ("district", "District"),
                            ("county", "County"),
                            ("lga", "Local Government Area"),
                            ("ward", "Ward"),
                            ("village", "Village / Settlement"),
                        ],
                        help_text="Administrative level of this area",
                    ),
                ),
                (
                    "geometry",
                    django.contrib.gis.db.models.fields.MultiPolygonField(
                        srid=4326,
                        null=True,
                        blank=True,
                        help_text="Geographic boundary as MultiPolygon (GeoJSON compatible)",
                    ),
                ),
                (
                    "centroid",
                    django.contrib.gis.db.models.fields.PointField(
                        srid=4326, null=True, blank=True, help_text="Center point of the geographic area"
                    ),
                ),
                (
                    "population",
                    models.PositiveIntegerField(null=True, blank=True, help_text="Estimated population (for prioritization)"),
                ),
                ("is_active", models.BooleanField(default=True, help_text="Whether this area is currently active/valid")),
                (
                    "parent",
                    models.ForeignKey(
                        to="geography.geographicarea",
                        on_delete=models.PROTECT,
                        null=True,
                        blank=True,
                        related_name="children",
                        help_text="Parent geographic area in hierarchy",
                    ),
                ),
            ],
            options={
                "verbose_name": "Geographic Area",
                "verbose_name_plural": "Geographic Areas",
                "ordering": ["country_code", "admin_level", "name"],
            },
        ),
        migrations.AddIndex(
            model_name="geographicarea",
            index=models.Index(fields=["country_code", "admin_level"], name="geo_area_country_admin_idx"),
        ),
        migrations.AddIndex(
            model_name="geographicarea",
            index=models.Index(fields=["parent"], name="geo_area_parent_idx"),
        ),
        migrations.AddConstraint(
            model_name="geographicarea",
            constraint=models.UniqueConstraint(
                fields=["name", "country_code", "admin_level", "parent"], name="unique_geographic_area"
            ),
        ),
    ]
