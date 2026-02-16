# Development Workflow Guide

## Getting Started

### 1. Initial Setup

```bash
# Clone the repository
git clone <repository-url>
cd agent-360-backend

# Install uv (if not already installed)
pip install uv
# Or: curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment with uv
uv venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Sync dependencies
uv sync

# Create .env file from template
cp .env.example .env

# Edit .env with your PostgreSQL credentials
# DB_NAME=agent360_db
# DB_USER=postgres
# DB_PASSWORD=your_password
# DB_HOST=localhost
# DB_PORT=5432
```

### Alternative: Using pip

If you prefer pip instead of `uv`:

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

### 2. Database Setup

```bash
# Run migrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser

# (Optional) Load sample data
python manage.py loaddata fixtures/sample_data.json
```

### 3. Run Development Server

```bash
python manage.py runserver
```

Access the application at `http://localhost:8000`
Admin panel at `http://localhost:8000/admin`

## Development Workflow

### Creating a New Feature

#### Step 1: Create a New App

```bash
python manage.py startapp apps.feature_name
```

#### Step 2: Define Models

Create `apps/feature_name/models.py`:

```python
from django.db import models
from core.models import BaseModel

class Feature(BaseModel):
    """Feature model."""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return self.name
```

#### Step 3: Create Migrations

```bash
python manage.py makemigrations apps.feature_name
python manage.py migrate
```

#### Step 4: Register in Admin

Create `apps/feature_name/admin.py`:

```python
from django.contrib import admin
from .models import Feature

@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']
```

#### Step 5: Create Serializers

Create `apps/feature_name/serializers.py`:

```python
from rest_framework import serializers
from .models import Feature

class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']
```

#### Step 6: Create Views

Create `apps/feature_name/views.py`:

```python
from rest_framework import viewsets
from .models import Feature
from .serializers import FeatureSerializer

class FeatureViewSet(viewsets.ModelViewSet):
    queryset = Feature.objects.all()
    serializer_class = FeatureSerializer
```

#### Step 7: Create URLs

Create `apps/feature_name/urls.py`:

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FeatureViewSet

router = DefaultRouter()
router.register(r'', FeatureViewSet)

app_name = 'feature_name'
urlpatterns = [
    path('', include(router.urls)),
]
```

#### Step 8: Register App

Add to `config/settings.py`:

```python
INSTALLED_APPS = [
    # ...
    'apps.feature_name',
]
```

Add to `config/urls.py`:

```python
urlpatterns = [
    # ...
    path('api/feature/', include('apps.feature_name.urls')),
]
```

#### Step 9: Write Tests

Create `apps/feature_name/tests.py`:

```python
from django.test import TestCase
from .models import Feature

class FeatureModelTest(TestCase):
    def setUp(self):
        self.feature = Feature.objects.create(
            name="Test Feature",
            description="Test description"
        )
    
    def test_feature_creation(self):
        self.assertEqual(self.feature.name, "Test Feature")
```

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.feature_name

# Run with verbose output
python manage.py test --verbosity=2

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Database Migrations

```bash
# Create new migration
python manage.py makemigrations

# Create empty migration
python manage.py makemigrations --empty apps.feature_name --name migration_name

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations

# Rollback to specific migration
python manage.py migrate apps.feature_name 0001

# Create migration for model changes
python manage.py makemigrations apps.feature_name
```

### Code Quality

#### Format Code with Black

```bash
# Using uv
uv pip install black
uv run black .

# Or directly
pip install black
black .
```

#### Lint with Flake8

```bash
# Using uv
uv pip install flake8
uv run flake8 .

# Or directly
pip install flake8
flake8 .
```

#### Type Checking with mypy

```bash
# Using uv
uv pip install mypy
uv run mypy .

# Or directly
pip install mypy
mypy .
```

#### Run All Quality Checks

```bash
# Using uv
uv run black . && uv run flake8 . && uv run mypy .

# Or directly
black . && flake8 . && mypy .
```

## Git Workflow

### Branch Naming Convention

```
feature/feature-name          # New feature
bugfix/bug-description        # Bug fix
hotfix/critical-issue         # Critical production fix
docs/documentation-update     # Documentation
refactor/refactoring-task     # Code refactoring
```

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Example:
```
feat(products): add product filtering by category

- Implement category filter in ProductViewSet
- Add category field to ProductSerializer
- Update API documentation

Closes #123
```

### Pull Request Process

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes and commit: `git commit -m "feat: description"`
3. Push to remote: `git push origin feature/my-feature`
4. Create pull request with description
5. Request code review
6. Address feedback
7. Merge to main

## Environment Variables

### Development (.env)

```
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production

DB_ENGINE=django.db.backends.postgresql
DB_NAME=agent360_db
DB_USER=postgres
DB_PASSWORD=dev_password
DB_HOST=localhost
DB_PORT=5432

ALLOWED_HOSTS=localhost,127.0.0.1
```

### Production

```
DEBUG=False
SECRET_KEY=<generate-secure-key>

DB_ENGINE=django.db.backends.postgresql
DB_NAME=<production-db-name>
DB_USER=<production-user>
DB_PASSWORD=<secure-password>
DB_HOST=<production-host>
DB_PORT=5432

ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
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

# Run shell
uv run python manage.py shell

# Run tests
uv run python manage.py test
```

### Using Django

```bash
# Create superuser
python manage.py createsuperuser

# Shell access
python manage.py shell

# Database shell
python manage.py dbshell

# Check for issues
python manage.py check

# Collect static files
python manage.py collectstatic

# Clear cache
python manage.py clear_cache

# Dump data
python manage.py dumpdata > backup.json

# Load data
python manage.py loaddata backup.json
```

## Debugging

### Django Debug Toolbar

```bash
uv pip install django-debug-toolbar
```

Add to `config/settings.py`:

```python
INSTALLED_APPS = [
    # ...
    'debug_toolbar',
]

MIDDLEWARE = [
    # ...
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = ['127.0.0.1']
```

### Logging

Check logs in `logs/django.log`:

```bash
tail -f logs/django.log
```

### Python Debugger

```python
import pdb; pdb.set_trace()  # Set breakpoint
```

Or use:

```python
breakpoint()  # Python 3.7+
```

## Performance Optimization

### Database Query Optimization

```python
# Use select_related for ForeignKey
products = Product.objects.select_related('category')

# Use prefetch_related for reverse relations
categories = Category.objects.prefetch_related('products')

# Use only() to limit fields
products = Product.objects.only('id', 'name')

# Use values() for aggregation
from django.db.models import Sum
totals = Product.objects.values('category').annotate(total=Sum('price'))
```

### Caching

```python
from django.views.decorators.cache import cache_page

@cache_page(60 * 5)  # Cache for 5 minutes
def product_list(request):
    pass
```

## Troubleshooting

### Database Connection Issues

```bash
# Check database connection
python manage.py shell
>>> from core.db import check_database_connection
>>> check_database_connection()

# Verify PostgreSQL is running
psql -U postgres -h localhost
```

### Migration Issues

```bash
# Show migration status
python manage.py showmigrations

# Fake migration if needed
python manage.py migrate --fake apps.feature_name 0001

# Rollback migration
python manage.py migrate apps.feature_name 0001
```

### Static Files Issues

```bash
# Collect static files
python manage.py collectstatic --clear --noinput

# Check static files
python manage.py findstatic css/style.css
```

### uv Issues

```bash
# Reinstall dependencies
uv sync --refresh

# Update uv itself
uv self update

# Check uv version
uv --version

# Clear cache
uv cache clean
```

## Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [PEP 8 Style Guide](https://pep8.org/)
- [uv Documentation](https://docs.astral.sh/uv/)
