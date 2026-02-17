# API Response & Request Handler

Standardized request/response handling system for Agent 360 API.

## 📁 Structure

```
core/api/
├── responses/          # Response handlers
│   ├── base.py        # Base response structure
│   ├── success.py     # Success response handlers
│   └── error.py       # Error response handlers
│
├── exceptions/         # Custom exceptions
│   ├── base.py        # Exception classes
│   └── handler.py     # Exception handler
│
├── serializers/        # Base serializers
│   └── base.py        # Base serializer classes
│
└── utils/             # Utilities
    ├── pagination.py  # Pagination classes
    └── validators.py  # Custom validators
```

---

## 🎯 Usage Examples

### 1. Success Responses

```python
from core.api.responses import SuccessResponse, APIResponse

# Simple success
def get_user(request, user_id):
    user = User.objects.get(id=user_id)
    serializer = UserSerializer(user)
    return SuccessResponse.retrieve(
        data=serializer.data,
        message="User retrieved successfully"
    )

# Create response
def create_user(request):
    serializer = UserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    return SuccessResponse.create(
        data=serializer.data,
        message="User created successfully",
        resource_id=user.id
    )

# List response
def list_users(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return SuccessResponse.list(
        data=serializer.data,
        message="Users retrieved successfully"
    )

# Update response
def update_user(request, user_id):
    user = User.objects.get(id=user_id)
    serializer = UserSerializer(user, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return SuccessResponse.update(
        data=serializer.data,
        message="User updated successfully"
    )

# Delete response
def delete_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.delete()
    return SuccessResponse.delete(
        message="User deleted successfully"
    )
```

### 2. Error Responses

```python
from core.api.responses import ErrorResponse

# Bad request
def create_user(request):
    if not request.data.get('email'):
        return ErrorResponse.bad_request(
            message="Email is required",
            errors=[{"field": "email", "message": "This field is required"}]
        )

# Not found
def get_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return ErrorResponse.resource_not_found(
            resource_type="User",
            resource_id=user_id
        )

# Unauthorized
def protected_view(request):
    if not request.user.is_authenticated:
        return ErrorResponse.unauthorized(
            message="Authentication required"
        )

# Forbidden
def admin_only_view(request):
    if not request.user.is_staff:
        return ErrorResponse.forbidden(
            message="Admin access required"
        )

# Validation error
def create_user(request):
    if User.objects.filter(email=request.data.get('email')).exists():
        return ErrorResponse.validation_error(
            message="Validation failed",
            errors=[{"field": "email", "message": "Email already exists"}]
        )
```

### 3. Using Custom Exceptions

```python
from core.api.exceptions import (
    ResourceNotFoundException,
    ValidationException,
    UnauthorizedException
)

# Raise custom exceptions (handled by exception handler)
def get_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise ResourceNotFoundException(
            resource_type="User",
            resource_id=user_id
        )
    
    serializer = UserSerializer(user)
    return SuccessResponse.retrieve(data=serializer.data)

# Validation exception
def create_user(request):
    if User.objects.filter(email=request.data.get('email')).exists():
        raise ValidationException("Email already exists")
    
    # ... create user

# Authorization exception
def protected_view(request):
    if not request.user.is_authenticated:
        raise UnauthorizedException("Authentication required")
    
    # ... process request
```

### 4. Pagination

```python
from core.api.utils import StandardPagination
from core.api.responses import APIResponse

class UserListView(APIView):
    pagination_class = StandardPagination
    
    def get(self, request):
        users = User.objects.all()
        paginator = self.pagination_class()
        paginated_users = paginator.paginate_queryset(users, request)
        serializer = UserSerializer(paginated_users, many=True)
        return paginator.get_paginated_response(serializer.data)
```

### 5. Base Serializers

```python
from core.api.serializers import BaseModelSerializer, AuditedSerializer

class UserSerializer(BaseModelSerializer, AuditedSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'created_date', 'created_by', 'last_modified_date', 'last_modified_by'
        ]

# List request with filtering
class UserListRequestSerializer(ListRequestSerializer):
    class Meta:
        ordering_fields = ['username', 'email', 'created_date']
```

---

## 📊 Response Formats

### Success Response

```json
{
    "success": true,
    "message": "Operation successful",
    "data": {
        "id": "001ABC123DEF456GHI",
        "username": "john_doe",
        "email": "john@example.com"
    },
    "meta": {
        "resource_id": "001ABC123DEF456GHI"
    }
}
```

### Error Response

```json
{
    "success": false,
    "message": "Validation failed",
    "error_code": "VALIDATION_ERROR",
    "errors": [
        {
            "field": "email",
            "message": "Email already exists"
        }
    ]
}
```

### Paginated Response

```json
{
    "success": true,
    "message": "Data retrieved successfully",
    "data": [...],
    "meta": {
        "pagination": {
            "current_page": 1,
            "page_size": 20,
            "total_count": 100,
            "total_pages": 5,
            "has_next": true,
            "has_previous": false
        }
    }
}
```

---

## 🔧 Configuration

### 1. Install Django REST Framework

```bash
pip install djangorestframework
```

### 2. Update `settings.py`

```python
INSTALLED_APPS = [
    # ...
    'rest_framework',
    # ...
]

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'core.api.exceptions.custom_exception_handler',
    'DEFAULT_PAGINATION_CLASS': 'core.api.utils.StandardPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
}
```

---

## 📝 Available Response Methods

### Success Methods

- `SuccessResponse.retrieve(data, message)` - GET single resource
- `SuccessResponse.list(data, message, meta)` - GET list
- `SuccessResponse.create(data, message, resource_id)` - POST create
- `SuccessResponse.update(data, message)` - PUT/PATCH update
- `SuccessResponse.delete(message)` - DELETE
- `SuccessResponse.login(data, message)` - Login
- `SuccessResponse.logout(message)` - Logout
- `SuccessResponse.register(data, message)` - Registration

### Error Methods

- `ErrorResponse.bad_request(message, errors, error_code)` - 400
- `ErrorResponse.unauthorized(message, error_code)` - 401
- `ErrorResponse.forbidden(message, error_code)` - 403
- `ErrorResponse.not_found(message, error_code, resource_type)` - 404
- `ErrorResponse.conflict(message, error_code, errors)` - 409
- `ErrorResponse.validation_error(message, errors, error_code)` - 422
- `ErrorResponse.server_error(message, error_code)` - 500

---

## 🛡️ Custom Exceptions

All exceptions in `core.api.exceptions.base` are automatically handled by the exception handler:

- `InvalidCredentialsException` - 401
- `TokenExpiredException` - 401
- `UnauthorizedException` - 401
- `PermissionDeniedException` - 403
- `ResourceNotFoundException` - 404
- `ValidationException` - 422
- `InternalServerException` - 500

---

## ✅ Best Practices

1. **Use appropriate response methods** for each operation type
2. **Raise exceptions** instead of returning error responses manually
3. **Include meaningful messages** in all responses
4. **Use error codes** for client-side error handling
5. **Validate input** using serializers before processing
6. **Use pagination** for list endpoints
7. **Include metadata** when relevant (pagination, resource IDs, etc.)

---

## 🔍 Testing

```python
from django.test import TestCase
from core.api.responses import SuccessResponse, ErrorResponse

class ResponseTestCase(TestCase):
    def test_success_response(self):
        response = SuccessResponse.retrieve(
            data={"id": "123"},
            message="Success"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])
    
    def test_error_response(self):
        response = ErrorResponse.not_found(
            message="User not found"
        )
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.data['success'])
```

---

## 📚 Additional Resources

- Django REST Framework: https://www.django-rest-framework.org/
- HTTP Status Codes: https://httpstatuses.com/
- REST API Best Practices: https://restfulapi.net/

---

For more details, check the individual module documentation in each folder.
