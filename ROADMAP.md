### OGA Local Service Atlas Tracker

**Goal:**  
Build an auditable, geospatial civic platform to track, verify, and monitor the status of public infrastructure and service delivery at the local government level across African contexts.

**Before you start, please ensure you have checked the project standard for this project [here]()**

This project must support:
- Urban and rural reporting environments
- Low-connectivity and mobile-first usage
- Citizen, government, and NGO data sources
- Strong provenance, verification, and accountability
- Long-term data quality and reuse

---

### Phase 1: Core Infrastructure & Data Modeling

#### 1.1 Geospatial Database Setup

- [ ] Set up PostgreSQL with PostGIS enabled
- [ ] Enable GeoJSON support for all spatial data
- [ ] Configure spatial indexes for efficient proximity queries

---

#### 1.2 Infrastructure Asset Model

- [ ] Define `InfrastructureAsset` model:
  - asset_id
  - asset_type (school, clinic, water_point, road, sanitation, electricity)
  - official_name (nullable)
  - geographic_point (GeoJSON)
  - geographic_area_id (FK)
  - data_source (official / NGO / community)
  - created_at / updated_at

- [ ] Enforce GeoJSON validation at the database level

---

#### 1.3 Geographic Area Model

- [ ] Define `GeographicArea` model:
  - name
  - country_code (ISO-3166)
  - admin_level (country / state / province / district / ward)
  - parent_area_id
  - optional geometry (PostGIS-ready)

📌 **Design Note:**  
Free-text locations are not allowed. All assets and reports must link to normalized geographic areas.

---

#### 1.4 Report Data Model

- [ ] Define `Report` model:
  - report_id
  - infrastructure_asset_id (nullable)
  - infrastructure_type
  - reported_status:
    - working
    - partially_working
    - broken
    - inaccessible
    - unknown
  - description
  - geographic_point (GeoJSON)
  - location_accuracy_meters (nullable)
  - reporter_type:
    - citizen
    - government_official
    - NGO
  - is_anonymous (boolean)
  - current_state:
    - Submitted
    - Under-Review
    - Verified
    - Resolved
  - reported_at
  - last_activity_at

---

#### 1.5 Evidence & Provenance Model

- [ ] Define `Evidence` model:
  - evidence_id
  - report_id
  - evidence_type (photo / document / link)
  - file_path or URL
  - file_hash
  - captured_at
  - uploaded_at
  - source_device (camera / upload)

📌 **Rule:**  
Every report must include at least one piece of evidence, unless explicitly flagged as low-confidence.

---

#### 1.6 Reporting Workflow State Machine

- [ ] Define valid transitions:
  - Submitted → Under-Review
  - Under-Review → Verified
  - Verified → Resolved
  - Under-Review → Rejected

- [ ] Enforce state transitions at the API level

---

### Phase 2: Data Ingestion & Official Sources

#### 2.1 Official Infrastructure Dataset Ingestion

- [ ] Define ingestion pipeline for official datasets:
  - source_url
  - data_owner
  - update_frequency
  - license
- [ ] Normalize ingested data into `InfrastructureAsset`
- [ ] Retain original source metadata for auditability

---

#### 2.2 Data Harmonization

- [ ] Match citizen reports to official assets using:
  - spatial proximity
  - asset type
  - name similarity (where available)
- [ ] Flag unmatched reports for review

---

### Phase 3: Citizen Submission & User Experience

#### 3.1 Citizen Submission Tool

- [ ] Mobile-responsive submission form
- [ ] Browser Geolocation API integration
- [ ] Manual pin adjustment on map
- [ ] Capture location accuracy metadata
- [ ] Photo upload with preview and compression
- [ ] Support anonymous reporting

📌 **Safety Note:**  
Personally identifiable information must not be publicly exposed by default.

📌 **Future-Proofing Note:**  
Support deferred submission when offline, with queued uploads upon reconnection.

---

#### 3.2 Interactive Map UI

- [ ] Integrate Leaflet or MapLibre
- [ ] Display infrastructure assets and reports as GeoJSON layers
- [ ] Color-code pins by:
  - reported status
  - verification state
- [ ] Visual distinction for stale reports

---

### Phase 4: Verification, Moderation & Trust

#### 4.1 Verification Metadata

- [ ] Track verification actions:
  - verified_by (user reference)
  - verification_method (site_visit / document / photo)
  - verified_at
  - verification_notes

---

#### 4.2 Duplicate & Abuse Detection

- [ ] Implement duplicate detection using:
  - spatial proximity thresholds
  - time windows
  - description similarity
- [ ] Allow moderators to merge or dismiss duplicate reports
- [ ] Rate-limit submissions per device/session

---

### Phase 5: Discrepancy Detection & Analysis

#### 5.1 Official vs Citizen Discrepancy Engine

- [ ] Compare official asset status with recent citizen reports
- [ ] Flag discrepancies such as:
  - official status = completed, citizen status = broken
- [ ] Prioritize discrepancies by:
  - number of reports
  - recency
  - severity

---

#### 5.2 Temporal Logic

- [ ] Track report freshness
- [ ] Flag outdated or inactive issues
- [ ] Allow re-verification of old reports

---

### Phase 6: Analytics, Dashboards & Alerts

#### 6.1 Analytics Dashboard

- [ ] Summary metrics per geographic area:
  - total reports
  - verified reports
  - resolved vs unresolved
- [ ] Trends over time
- [ ] Filter by asset type and status

---

#### 6.2 Subscription & Alert System

- [ ] Allow users to follow:
  - specific infrastructure assets
  - geographic areas
- [ ] Notify subscribers on:
  - status changes
  - verification updates

---

### Phase 7: API, Validation & Quality Assurance

#### 7.1 Public & Admin APIs

- [ ] CRUD endpoints for:
  - Infrastructure Assets
  - Reports
  - Evidence
  - Geographic Areas
- [ ] Read-only public endpoints for map and analytics
- [ ] Role-based access control for moderation actions

---

#### 7.2 Validation Rules

- [ ] Enforce Geo JSON validity
- [ ] Validate state transitions
- [ ] Prevent orphaned evidence
- [ ] Enforce country and area consistency

---

#### 7.3 Automated Testing

- [ ] Unit tests for models and state machine
- [ ] Integration tests for report lifecycle
- [ ] CI enforcement via GitHub Actions

---

### Phase 8: Finalization & Handover

- [ ] Populate demo data for at least one local government area
- [ ] Include:
  - urban example
  - rural example
- [ ] Deploy live demo environment
- [ ] Produce:
  - ARCHITECTURE.md
  - DATA_MODEL_DECISIONS.md
  - CONTRIBUTING.md
- [ ] Identify at least 5 “Good First Issues”:
  - Add a new asset type
  - Improve duplicate detection
  - UI performance optimizations
  - Verification workflow improvements
  - Accessibility enhancements

---

### Final Checks

- [ ] All spatial data uses Geo JSON
- [ ] Every report has evidence and provenance
- [ ] Verification actions are auditable
- [ ] Duplicate and stale reports are handled
- [ ] Discrepancies are detectable and queryable
- [ ] Dashboard reflects real data quality
- [ ] API is documented and test-covered
