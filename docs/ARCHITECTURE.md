# OGA Local Service Atlas - Architecture

## Overview

The OGA Local Service Atlas is a geospatial civic platform designed to track, verify, and monitor public infrastructure and service delivery across African local government contexts.

## Tech Stack

| Layer | Technology | Justification |
|-------|------------|---------------|
| **Backend Framework** | Django 5.x + Django REST Framework | Mature ecosystem, built-in admin, excellent GeoDjango support |
| **Database** | PostgreSQL 16 + PostGIS 3.4 | Industry-standard for geospatial data, required by project spec |
| **API Documentation** | drf-spectacular (OpenAPI 3.0) | Automatic OpenAPI docs as required by project standards |
| **Authentication** | JWT (djangorestframework-simplejwt) | Stateless auth suitable for mobile-first clients |
| **Cache** | Redis 7 | Session storage, caching, future Celery broker |
| **Containerization** | Docker + Docker Compose | Reproducible development environment |
| **CI/CD** | GitHub Actions | Automated linting, testing, and Docker builds |

## Project Structure

```
oga-local-service-atlas/
├── .github/workflows/      # CI/CD pipelines
├── backend/
│   ├── apps/
│   │   ├── core/           # Base models, utilities
│   │   ├── geography/      # GeographicArea model
│   │   ├── infrastructure/ # InfrastructureAsset model
│   │   └── reports/        # Report, Evidence, Verification models
│   ├── config/             # Django settings, URLs, WSGI
│   ├── Dockerfile
│   ├── manage.py
│   ├── pyproject.toml      # Linting/formatting config
│   └── requirements.txt
├── docs/                   # Documentation
├── docker-compose.yml
├── .env.example
└── README.md
```

## Data Models

### Phase 1 Models (Core Infrastructure & Data Modeling)

#### GeographicArea (Phase 1.3)
Normalized administrative divisions. **No free-text locations allowed**.

```
GeographicArea
├── id (UUID)
├── name
├── country_code (ISO 3166-1 alpha-3)
├── admin_level (country/state/district/ward/etc.)
├── parent_id (FK to self)
├── geometry (MultiPolygon, nullable)
├── centroid (Point, nullable)
├── population (nullable)
├── data_source (official/ngo/community)
├── source_url
└── timestamps
```

#### InfrastructureAsset (Phase 1.2)
Public infrastructure assets with geospatial location.

```
InfrastructureAsset
├── id (UUID)
├── asset_type (school/clinic/water_point/road/etc.)
├── official_name (nullable)
├── local_name
├── location (Point, required)
├── geographic_area_id (FK, required)
├── condition (functional/partially_functional/non_functional/etc.)
├── data_source
├── is_verified
└── timestamps
```

#### Report (Phase 1.4)
Citizen/official reports about infrastructure status.

```
Report
├── id (UUID)
├── infrastructure_asset_id (FK, nullable)
├── infrastructure_type
├── reported_status (working/partially_working/broken/etc.)
├── description
├── location (Point)
├── location_accuracy_meters (nullable)
├── reporter_type (citizen/government_official/ngo)
├── reporter_id (FK to User, nullable)
├── is_anonymous
├── current_state (submitted/under_review/verified/rejected/resolved)
├── reported_at
└── last_activity_at
```

#### Evidence (Phase 1.5)
Evidence attached to reports with provenance tracking.

```
Evidence
├── id (UUID)
├── report_id (FK)
├── evidence_type (photo/video/document/link)
├── file (FileField, nullable)
├── url (nullable)
├── file_hash (SHA-256)
├── captured_at (nullable)
├── uploaded_at
└── source_device
```

### State Machine (Phase 1.6)

Report workflow states and valid transitions:

```
Submitted → Under-Review → Verified → Resolved
                       ↘ Rejected
```

## API Design

### Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/health/` | Health check |
| `GET/POST /api/v1/geography/areas/` | Geographic areas CRUD |
| `GET /api/v1/geography/areas/geojson/` | GeoJSON export |
| `GET/POST /api/v1/infrastructure/assets/` | Infrastructure assets CRUD |
| `GET /api/v1/infrastructure/assets/geojson/` | GeoJSON export |
| `GET/POST /api/v1/reports/` | Reports CRUD |
| `POST /api/v1/reports/{id}/transition/` | State transitions |
| `GET /api/v1/reports/geojson/` | GeoJSON export |
| `GET /api/docs/` | Swagger UI |
| `GET /api/redoc/` | ReDoc |

### GeoJSON Support

All spatial data is served as GeoJSON via dedicated endpoints:
- `/geojson/` actions on ViewSets return GeoJSON FeatureCollections
- Uses `djangorestframework-gis` for serialization

## Design Decisions

### 1. No Free-Text Locations
All assets and reports must link to a normalized `GeographicArea`. This ensures:
- Data quality and consistency
- Queryability across administrative levels
- Prevention of duplicates and typos

### 2. UUID Primary Keys
All models use UUIDs instead of auto-incrementing integers:
- Prevents enumeration attacks
- Enables distributed ID generation
- Better for API exposure

### 3. Audit Trail
All models inherit from `AuditableModel` which includes:
- `data_source` (provenance tracking)
- `source_url` (reference)
- `created_at` / `updated_at` timestamps

### 4. State Machine
Reports follow a strict state machine pattern:
- Transitions are validated at the model level
- Invalid transitions raise `ValidationError`
- Supports future workflow customization

### 5. Evidence Integrity
Evidence files are hashed (SHA-256) on upload:
- Ensures file integrity
- Detects tampering
- Supports verification workflows

## Development Setup

```bash
# Clone and setup
git clone https://github.com/OpenGovAfrica/oga-local-service-atlas.git
cd oga-local-service-atlas
cp .env.example .env

# Start services
docker compose up -d

# Run migrations
docker compose exec backend python manage.py migrate

# Create superuser
docker compose exec backend python manage.py createsuperuser

# Access
# API: http://localhost:8000/api/docs/
# Admin: http://localhost:8000/admin/
```

## Future Considerations

- **Phase 2**: Official data ingestion pipelines
- **Phase 3**: Mobile-first citizen submission UI
- **Phase 4**: Verification and moderation tooling
- **Phase 5**: Discrepancy detection between official and citizen data
- **Phase 6**: Analytics dashboards and alerts
