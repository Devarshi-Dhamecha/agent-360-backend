# Agent 360 Backend

Django backend with PostgreSQL database integration.

## Setup

### Prerequisites
- Python 3.12+
- PostgreSQL 12+

### Installation

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -e .
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
└── .env.example         # Environment variables template
```

## Dependencies

- **django**: Web framework
- **psycopg**: PostgreSQL adapter
- **python-dotenv**: Environment variable management
- **gunicorn**: Production WSGI server
