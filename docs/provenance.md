## Provenance and Auditability

**If provenance is not explicit and queryable, it does not exist.**  
This document specifies how provenance is modeled across the OGA Local Service Atlas Tracker and what is required of contributors when adding or extending data models.

The goals are:

- **Traceability**: Every record can be traced back to a source, an actor, and a time.
- **Auditability**: Reviewers can reconstruct who did what, when, and based on which evidence.
- **Comparability**: Official and community data can coexist and be compared without ambiguity.

---

## Core Provenance Concepts

- **Source**: Where the data comes from (official government, NGO, community, research, etc.).
- **Actor**: The user or system that submitted or modified the data.
- **Timestamps**: When the data was created and last updated, plus domain-specific times (e.g., reported_at, verified_at, uploaded_at).
- **Evidence**: Files, links, or other artifacts that support a claim.

All core domain models MUST expose these concepts in a way that is:

- **Explicit** in the schema (no “implied” provenance).
- **Queryable** via the database and API.
- **Documented** in this file and in `docs/ARCHITECTURE.md` when new models are introduced.

---

## Base Models and Shared Fields

The `apps.core.models` module defines shared building blocks:

- **`UUIDModel`**: UUID primary keys (non-enumerable, suitable for public APIs).
- **`TimestampedModel`**:  
  - `created_at` – when the record was first created.  
  - `updated_at` – when the record was last modified.
- **`BaseModel`**: Combines `UUIDModel` + `TimestampedModel`.
- **`DataSourceType` (enum)**:  
  - `official` – Official government source  
  - `ngo` – NGO / Civil Society  
  - `community` – Community reported  
  - `research` – Research / Academic
- **`AuditableModel`** (extends `BaseModel`):  
  - `data_source` – required, enumerated source of the entry.  
  - `source_url` – optional URL pointing to the upstream dataset or document.  
  - `source_notes` – free-text notes about how/where the data was obtained.

Any model that represents **persistent civic data** (e.g., geographic areas, infrastructure assets) is expected to inherit from `AuditableModel` so that `data_source`, `source_url`, and `source_notes` are always available.

---

## Model-by-Model Provenance

### GeographicArea

- **Model**: `apps.geography.models.GeographicArea`  
- **Base**: `AuditableModel`

- **Source**:
  - `data_source` – who provided the boundary data (official shapefile, NGO survey, etc.).
  - `source_url` – link to official or canonical dataset when available.
  - `source_notes` – notes about import pipeline, manual corrections, or versioning.
- **Timestamps**:
  - `created_at`, `updated_at` – from `TimestampedModel`.
- **Actor**:
  - The creator/updater is inferred via the Django admin or ingestion process, and can be recovered from audit logs / Git history for migration files.

**Query examples**:

- All geographic areas sourced from official data:

  ```sql
  SELECT *
  FROM geography_geographicarea
  WHERE data_source = 'official';
  ```

- Recently updated areas for a specific country and source:

  ```sql
  SELECT *
  FROM geography_geographicarea
  WHERE country_code = 'NGA'
    AND data_source = 'ngo'
    AND updated_at >= NOW() - INTERVAL '30 days';
  ```

---

### InfrastructureAsset

- **Model**: `apps.infrastructure.models.InfrastructureAsset`  
- **Base**: `AuditableModel`

- **Source**:
  - `data_source` – origin of the asset record (official registry, NGO mapping project, community mapping, etc.).
  - `source_url` – link to the official registry entry or dataset, if applicable.
  - `source_notes` – notes about field verification, manual correction, or import details.
- **Timestamps**:
  - `created_at`, `updated_at` – from `TimestampedModel`.
  - `condition_verified_at` – when the asset’s condition was last verified.
- **Actor**:
  - For now, actor is associated with the system context (admin user, ingestion pipeline). Future phases may introduce explicit user attribution on asset creation/updates.

**Query examples**:

- All assets from official sources with non-functional status:

  ```sql
  SELECT *
  FROM infrastructure_infrastructureasset
  WHERE data_source = 'official'
    AND condition IN ('non_functional', 'abandoned');
  ```

- Community-sourced assets that have never been verified:

  ```sql
  SELECT *
  FROM infrastructure_infrastructureasset
  WHERE data_source = 'community'
    AND is_verified = FALSE;
  ```

---

### Report

- **Model**: `apps.reports.models.Report`  
- **Base**: `BaseModel`

Reports track **who reported what, when, and from where**:

- **Source**:
  - `reporter_type` – structured enumeration of who submitted the report:
    - `citizen`
    - `government_official`
    - `ngo`
  - In future phases, additional reporter types (e.g., `system`) can be added to distinguish automated sources.
- **Actor**:
  - `reporter` – FK to `AUTH_USER_MODEL` (nullable).
  - `is_anonymous` – whether the report was submitted anonymously.
  - The `ReportViewSet.perform_create` method sets `reporter` to the authenticated user when `is_anonymous` is `False`, ensuring that non-anonymous reports are attributable.
- **Timestamps**:
  - `reported_at` – when the report was first submitted.
  - `last_activity_at` – updated whenever the report changes (including workflow transitions).

**Query examples**:

- All reports submitted by NGOs in the last 7 days:

  ```sql
  SELECT *
  FROM reports_report
  WHERE reporter_type = 'ngo'
    AND reported_at >= NOW() - INTERVAL '7 days';
  ```

- Anonymous citizen reports about broken infrastructure:

  ```sql
  SELECT *
  FROM reports_report
  WHERE reporter_type = 'citizen'
    AND is_anonymous = TRUE
    AND reported_status = 'broken';
  ```

---

### Evidence

- **Model**: `apps.reports.models.Evidence`  
- **Base**: `BaseModel`

Evidence provides **verifiable backing** for reports:

- **Source**:
  - `evidence_type` – what kind of artifact this is (photo, video, document, audio, link).
  - `file` / `url` – the actual content or pointer to it.
  - `source_device` – how the evidence was captured:
    - `camera`, `upload`, `screenshot`, `other`.
- **Actor**:
  - Implicitly tied to the report’s reporter and any authenticated uploader via API permissions.
- **Timestamps**:
  - `captured_at` – when the evidence was captured (e.g., from EXIF metadata or user input).
  - `uploaded_at` – when the evidence was uploaded to the system.
- **Integrity**:
  - `file_hash` – SHA-256 hash computed on save.
  - `file_size_bytes` – size of the uploaded file in bytes.

**Constraints**:

- Either `file` **or** `url` must be provided (but not both); enforced in `Evidence.clean()`.
- Evidence is always linked to a `Report` via the `report` FK.

**Query examples**:

- All photo evidence uploaded in the last 24 hours:

  ```sql
  SELECT *
  FROM reports_evidence
  WHERE evidence_type = 'photo'
    AND uploaded_at >= NOW() - INTERVAL '1 day';
  ```

---

### Verification

- **Model**: `apps.reports.models.Verification`  
- **Base**: `BaseModel`

Verification actions record **who verified what, how, and with what outcome**:

- **Source / Method**:
  - `verification_method` – structured enumeration:
    - `site_visit`, `document`, `photo`, `cross_reference`, `other`.
  - `verification_notes` – free-text explanation of the process and findings.
- **Actor**:
  - `verified_by` – FK to `AUTH_USER_MODEL` (nullable).
  - Set automatically in `VerificationViewSet.perform_create` to the current authenticated user.
- **Timestamps**:
  - `verified_at` – when the verification was performed.

**Query examples**:

- All confirmed verifications for a specific report:

  ```sql
  SELECT *
  FROM reports_verification
  WHERE report_id = '<uuid>'
    AND is_confirmed = TRUE;
  ```

---

## Required Practices for New Models

When introducing new models that represent persistent civic or workflow data:

- **Use `AuditableModel`** for:
  - Canonical data (geographic layers, infrastructure registries, reference tables).
- **At minimum, use `BaseModel` plus explicit provenance fields** for:
  - Transactional/workflow entities (reports, verifications, moderation actions).

New models MUST:

- Include a clear **`source`** concept (e.g., `data_source`, `actor_type`, or similar).
- Capture relevant **timestamps** (created, updated, domain-specific).
- Attribute actions to an **actor** (FK to user, or structured system identifier).
- Be documented in:
  - `docs/ARCHITECTURE.md` (high-level), and
  - `docs/provenance.md` (this file) with a short section like the ones above.

---

## Provenance in APIs

The REST API surfaces provenance fields so that clients can:

- Filter and aggregate by source (`data_source`, `reporter_type`, `verification_method`).
- Inspect timestamps (`reported_at`, `uploaded_at`, `verified_at`).
- Attribute actions to users where appropriate (`reporter`, `verified_by`).

When adding or updating endpoints:

- **Do not hide** provenance fields unless there is a strong privacy reason.
- Ensure that filters for provenance fields are exposed where useful (e.g., filtering reports by `reporter_type` or `current_state`).
- Reflect any new provenance behavior in the OpenAPI schema and in this document.

