## Geographic Modeling and Normalization

This document explains how geographic data is represented, normalized, and enforced in the OGA Local Service Atlas Tracker.

The core principles are:

- **No free‑text locations** in domain models or APIs.
- **Normalized geographic entities** as the canonical representation of place.
- **PostGIS + GeoDjango** as the source of truth for spatial queries.
- **GeoJSON** as the interchange format for clients.

---

## GeographicArea Model

The `GeographicArea` model in `apps.geography.models` is the canonical representation of administrative geography.

Key properties:

- Hierarchical administrative units (country, state, district, ward, village, etc.).
- Optional geometries for polygons and centroids.
- Provenance tracking via `AuditableModel`.

Field overview:

- `name` – official name of the area.
- `country_code` – ISO 3166‑1 alpha‑3 country code (e.g., `NGA`, `KEN`, `ZAF`).
- `admin_level` – one of the values from `AdminLevel` (`country`, `state`, `district`, `ward`, etc.).
- `parent` – FK to `GeographicArea`, forming a tree/hierarchy.
- `geometry` – `MultiPolygonField` (SRID 4326) for boundaries.
- `centroid` – `PointField` (SRID 4326) for quick point‑in‑area style queries.
- `population` – optional population metadata.
- `is_active` – whether the area is currently in use.
- Provenance fields from `AuditableModel`: `data_source`, `source_url`, `source_notes`, `created_at`, `updated_at`.

Uniqueness and indexing:

- Unique constraint on `(name, country_code, admin_level, parent)` prevents duplicate areas at the same level and hierarchy position.
- Indexes on `country_code`, `admin_level`, and `parent` support fast navigation and filtering.

---

## No Free‑Text Locations

The system is designed around **normalized** locations:

- **In models**:
  - `GeographicArea` is the only place where administrative names are stored as free text.
  - `InfrastructureAsset` links to `GeographicArea` via a required FK (`geographic_area`).
  - Reports use a precise point `location` and can be spatially joined to `GeographicArea` for analysis.
- **In APIs**:
  - Clients should send coordinates (GeoJSON Point) and/or identifiers for known areas.
  - Free‑text descriptions such as “near the big market in town” must not be used as location fields (they may appear in narrative `description` fields, but not as a substitute for coordinates or area references).

This rule is enforced through:

- Schema design:
  - `InfrastructureAsset.geographic_area` is non‑nullable and uses `on_delete=PROTECT`, ensuring every asset belongs to a valid area and that areas cannot be silently deleted.
- API design:
  - Geography, infrastructure, and reports endpoints expose structured spatial fields and do not expose any “city”, “state”, or “location_name” free‑text fields.
- Contribution guidelines:
  - `docs/CONTRIBUTING.md` explicitly prohibits free‑text locations.

---

## Infrastructure Assets and Geographic Areas

**Model**: `apps.infrastructure.models.InfrastructureAsset`

Geographic fields:

- `location` – required `PointField` (SRID 4326) representing the exact location of the asset.
- `geographic_area` – required FK to `GeographicArea`, ensuring every asset is anchored in the normalized geography hierarchy.

Implications:

- Assets can always be:
  - Aggregated by admin level (country, state, district, ward, etc.).
  - Filtered by `GeographicArea` (e.g., all assets in a specific ward).
  - Cross‑referenced with external boundary datasets (since they share SRID 4326).

Example queries:

- All clinics in a specific district:

  ```sql
  SELECT a.*
  FROM infrastructure_infrastructureasset AS a
  JOIN geography_geographicarea AS g
    ON a.geographic_area_id = g.id
  WHERE g.name = 'Example District'
    AND g.admin_level = 'district'
    AND a.asset_type = 'clinic';
  ```

---

## Reports and Spatial Normalization

**Model**: `apps.reports.models.Report`

Geographic fields:

- `location` – required `PointField` (SRID 4326) representing the reported location.
- `location_accuracy_meters` – optional accuracy metadata.
- `infrastructure_asset` – optional FK to `InfrastructureAsset`, which indirectly ties the report to a `GeographicArea`.

Normalization rules:

- Every report must:
  - Provide a coordinate (`location`).
  - Optionally link to an existing asset (which is itself linked to a `GeographicArea`).
- For analytics and moderation, reports can be:
  - **Spatially joined** to `GeographicArea` using PostGIS (e.g., `ST_Contains(geography_area.geometry, report.location)`).
  - Grouped by admin level, even when the report is not yet linked to a known asset.

Future phases may introduce:

- An explicit `geographic_area` FK on `Report` or a materialized view that pre‑computes area assignments using spatial joins.
- Database‑level constraints or background jobs to ensure all reports fall within a known `GeographicArea` where boundaries are available.

---

## GeoJSON and SRID

All spatial fields use SRID 4326 (WGS84) and are exposed as **GeoJSON** through the API:

- `GeographicArea`:
  - `GET /api/v1/geography/areas/geojson/` – GeoJSON FeatureCollection of areas.
- `InfrastructureAsset`:
  - `GET /api/v1/infrastructure/assets/geojson/` – GeoJSON FeatureCollection of assets.
- `Report`:
  - `GET /api/v1/reports/geojson/` – GeoJSON FeatureCollection of reports.

When adding new spatial endpoints:

- Use `djangorestframework-gis` and `GeoFeatureModelSerializer`.
- Maintain SRID 4326 for all persistent spatial fields.
- Ensure new endpoints clearly document which geometry field they expose.

---

## Expectations for Contributors

When introducing new models or APIs that involve geography:

- **Do not** introduce free‑text location fields that act as primary location references.
- **Do**:
  - Reference `GeographicArea` where an administrative unit is required.
  - Use `PointField`/`MultiPolygonField` with SRID 4326 for spatial data.
  - Expose spatial data as GeoJSON in API endpoints.
  - Document any new geographic behavior or constraints in:
    - `docs/ARCHITECTURE.md` (high‑level), and
    - `docs/geography.md` (this file, with a short section for new models or flows).

