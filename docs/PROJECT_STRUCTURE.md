# Project Structure Guide

## Directory Layout

```
agent-360-backend/
├── config/                          # Django configuration
│   ├── __init__.py
│   ├── settings.py                  # Django settings (DB, apps, middleware)
│   ├── urls.py                      # Main URL routing
│   ├── wsgi.py                      # WSGI application (production)
│   └── asgi.py                      # ASGI application (async)
│
├── core/                            # Core application (shared utilities)
│   ├── migrations/                  # Database migrations
│   │   └── __init__.py
│   ├── __init__.py
│   ├── admin.py                     # Django admin configuration
│   ├── apps.py                      # App configuration
│   ├── models.py                    # Core data models
│   ├── views.py                     # Core views/API endpoints
│   ├── serializers.py               # DRF serializers (if using DRF)
│   ├── urls.py                      # Core app URL routing
│   ├── db.py                        # Database utilities
│   ├── constants.py                 # Application constants
│   ├── exceptions.py                # Custom exceptions
│   └── tests.py                     # Unit tests
│
├── apps/                            # Feature-specific applications
│   ├── users/                       # User management app
│   │   ├── migrations/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   ├── services.py              # Business logic
│   │   ├── permissions.py           # Custom permissions
│   │   └── tests.py
│   │
│   ├── products/                    # Product management app
│   │   ├── migrations/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   ├── services.py
│   │   └── tests.py
│   │
│   └── __init__.py
│
├── utils/                           # Shared utilities across apps
│   ├── __init__.py
│   ├── decorators.py                # Custom decorators
│   ├── helpers.py                   # Helper functions
│   ├── validators.py                # Custom validators
│   ├── pagination.py                # Pagination utilities
│   └── exceptions.py                # Shared exceptions
│
├── static/                          # Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── images/
│
├── media/                           # User-uploaded files
│   └── uploads/
│
├── templates/                       # HTML templates
│   ├── base.html
│   └── core/
│
├── logs/                            # Application logs
│   └── django.log
│
├── tests/                           # Integration and E2E tests
│   ├── __init__.py
│   ├── conftest.py                  # Pytest configuration
│   ├── factories.py                 # Test data factories
│   └── integration/
│
├── docs/                            # Documentation
│   ├── PROJECT_STRUCTURE.md         # This file
│   ├── CODE_STANDARDS.md            # Code standards
│   ├── API_DOCUMENTATION.md         # API docs
│   ├── DATABASE_SCHEMA.md           # Database schema
│   └── DEPLOYMENT.md                # Deployment guide
│
├── scripts/                         # Utility scripts
│   ├── __init__.py
│   ├── seed_db.py                   # Database seeding
│   └── cleanup.py                   # Cleanup tasks
│
├── .env.example                     # Environment variables template
├── .gitignore                       # Git ignore rules
├── .python-version                  # Python version
├── manage.py                        # Django management script
├── pyproject.toml                   # Project dependencies
└── README.md                        # Project README
```

## Folder Descriptions

### `config/`
Contains all Django configuration files. This is the heart of the project settings.
- **settings.py**: Database, installed apps, middleware, logging
- **urls.py**: Main URL router
- **wsgi.py**: Production WSGI server entry point
- **asgi.py**: Async server entry point

### `core/`
Core application for shared functionality and models used across the project.
- **models.py**: Base models, common models
- **views.py**: Core API endpoints
- **db.py**: Database utilities and helpers
- **constants.py**: Application-wide constants
- **exceptions.py**: Custom exception classes

### `apps/`
Feature-specific Django applications. Each app is self-contained and reusable.
- Each app follows Django conventions
- Contains models, views, serializers, URLs specific to that feature
- **services.py**: Business logic layer (recommended pattern)

### `utils/`
Shared utilities used across multiple apps.
- Decorators, validators, helpers
- Pagination, pagination utilities
- Shared exception handling

### `static/`
Static files served by the web server (CSS, JavaScript, images).

### `media/`
User-uploaded files and dynamic content.

### `templates/`
HTML templates for rendering views.

### `logs/`
Application log files (created at runtime).

### `tests/`
Test suite for integration and end-to-end testing.
- **conftest.py**: Pytest configuration and fixtures
- **factories.py**: Test data factories using factory_boy

### `docs/`
Project documentation including this file.

### `scripts/`
Utility scripts for database seeding, cleanup, etc.

## Creating a New App

When adding a new feature, create a new app:

```bash
python manage.py startapp apps.feature_name
```

Then add to `INSTALLED_APPS` in `config/settings.py`:

```python
INSTALLED_APPS = [
    # ...
    'apps.feature_name',
]
```

## File Naming Conventions

- **Python files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions/variables**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Django models**: Singular noun (e.g., `User`, `Product`)
- **Django views**: Plural or descriptive (e.g., `UserListView`, `ProductDetailView`)

## Import Organization

Within each file, organize imports in this order:

1. Standard library imports
2. Third-party imports
3. Django imports
4. Local app imports

Example:
```python
import os
import json
from datetime import datetime

import requests
from rest_framework import serializers

from django.db import models
from django.contrib.auth.models import User

from core.models import BaseModel
from .models import Product
```
