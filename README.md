# Agent 360 Backend

Django backend with PostgreSQL database integration.

## Setup

### Prerequisites
- Python 3.12+
- PostgreSQL 12+
- `uv` package manager

### Installation with `uv`

1. Install `uv` (if not already installed):
```bash
# Using pip
pip install uv

# Or using your system package manager
# macOS: brew install uv
# Linux: curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Create virtual environment and install dependencies:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv sync
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your PostgreSQL credentials
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create superuser:
```bash
python manage.py createsuperuser
```

6. Run development server:
```bash
python manage.py runserver
```

### Alternative: Installation with pip

If you prefer using pip instead of `uv`:

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

## Database

PostgreSQL is configured as the default database. Connection settings are managed via environment variables in `.env`.

### Database Operations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Check database connection
python manage.py shell
>>> from core.db import check_database_connection
>>> check_database_connection()
```

## Common Commands

### Using `uv`

```bash
# Sync dependencies
uv sync

# Run Python commands
uv run python manage.py migrate
uv run python manage.py runserver

# Add new dependency
uv pip install package-name

# Update dependencies
uv sync --upgrade
```

### Using Django

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Access Django shell
python manage.py shell

# Run tests
python manage.py test
```

## Project Structure

```
.
├── config/              # Django configuration
│   ├── settings.py      # Settings with PostgreSQL config
│   ├── urls.py          # URL routing
│   ├── wsgi.py          # WSGI application
│   └── asgi.py          # ASGI application
├── core/                # Core utilities
│   └── db.py            # Database utilities
├── manage.py            # Django management script
├── pyproject.toml       # Project dependencies
├── .env.example         # Environment variables template
└── docs/                # Documentation
    ├── README.md        # Documentation index
    ├── PROJECT_STRUCTURE.md
    ├── CODE_STANDARDS.md
    ├── DEVELOPMENT_WORKFLOW.md
    ├── API_DOCUMENTATION.md
    ├── DATABASE_SCHEMA.md
    └── DEPLOYMENT.md
```

## Dependencies

- **django**: Web framework
- **psycopg**: PostgreSQL adapter
- **python-dotenv**: Environment variable management
- **gunicorn**: Production WSGI server

## Documentation

For comprehensive guides on development, deployment, and best practices, see the [docs/README.md](./docs/README.md) file.

Key documentation files:
- **[PROJECT_STRUCTURE.md](./docs/PROJECT_STRUCTURE.md)** - Folder layout and organization
- **[CODE_STANDARDS.md](./docs/CODE_STANDARDS.md)** - Coding standards and best practices
- **[DEVELOPMENT_WORKFLOW.md](./docs/DEVELOPMENT_WORKFLOW.md)** - Development guide
- **[API_DOCUMENTATION.md](./docs/API_DOCUMENTATION.md)** - API design and endpoints
- **[DATABASE_SCHEMA.md](./docs/DATABASE_SCHEMA.md)** - Database design
- **[DEPLOYMENT.md](./docs/DEPLOYMENT.md)** - Deployment guide
