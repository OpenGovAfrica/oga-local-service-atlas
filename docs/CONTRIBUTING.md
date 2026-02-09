# Contributing to OGA Local Service Atlas

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Git
- Python 3.12+ (for local development without Docker)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/OpenGovAfrica/oga-local-service-atlas.git
   cd oga-local-service-atlas
   ```

2. **Copy environment file**
   ```bash
   cp .env.example .env
   ```

3. **Start services with Docker**
   ```bash
   docker compose up -d
   ```

4. **Run migrations**
   ```bash
   docker compose exec backend python manage.py migrate
   ```

5. **Create a superuser**
   ```bash
   docker compose exec backend python manage.py createsuperuser
   ```

6. **Access the application**
   - API Docs: http://localhost:8000/api/docs/
   - Admin: http://localhost:8000/admin/

### Local Development (without Docker)

If you prefer to run without Docker:

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Set environment variables (requires PostgreSQL + PostGIS locally)
export DATABASE_URL=postgis://user:password@localhost:5432/oga_atlas
export SECRET_KEY=your-secret-key

# Run migrations and server
cd backend
python manage.py migrate
python manage.py runserver
```

## Code Standards

### Linting and Formatting

We use **Ruff** for linting and **Black** for formatting. These are enforced in CI.

```bash
# Check linting
ruff check backend/

# Format code
black backend/

# Or use pre-commit hooks
pip install pre-commit
pre-commit install
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `test:` - Adding or updating tests
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

Examples:
```
feat: add geographic area API endpoints
fix: correct state transition validation in reports
docs: update API documentation for evidence upload
```

### Testing

All new features must include tests. We use pytest with Django.

```bash
# Run tests
cd backend
pytest

# Run with coverage
pytest --cov=apps --cov-report=term-missing
```

Minimum coverage requirement: **70%** for business logic.

## Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feat/your-feature-name
   ```

2. **Make your changes**
   - Write clean, documented code
   - Add tests for new functionality
   - Update documentation if needed

3. **Run checks locally**
   ```bash
   ruff check backend/
   black --check backend/
   pytest
   ```

4. **Submit a pull request**
   - Link to related issue (e.g., "Closes #12")
   - Provide clear description of changes
   - Include screenshots for UI changes

5. **Review process**
   - At least one peer review required
   - Maintainer approval for merge
   - All CI checks must pass

## Data Model Changes

Changes to data models require:

1. Written justification in the PR description
2. Migration files included
3. Documentation updated in `docs/ARCHITECTURE.md`
4. Tests for new model behavior

## Geographic Data Guidelines

- **No free-text locations**: All locations must reference a `GeographicArea`
- **GeoJSON format**: All spatial data uses GeoJSON (SRID 4326)
- **Validation**: Geographic data must be validated at both API and database levels

## Evidence and Provenance

- All data entries must have `data_source` specified
- Evidence files are hashed for integrity
- Reports require evidence unless flagged as low-confidence

## Getting Help

- Check existing issues before creating new ones
- Ask questions in discussions or public channels
- Tag maintainers: @tamaradenyefa @opengov-africa

## Code of Conduct

Please read and follow our [Code of Conduct](https://github.com/OpenGovAfrica/.github/blob/main/CODE_OF_CONDUCT.md).

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
