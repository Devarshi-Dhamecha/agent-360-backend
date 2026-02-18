# API Implementation Examples

Complete examples showing how to implement API endpoints using the standardized response system.

---

## Example 1: User Management API

### views.py

```python
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from core.api.responses import SuccessResponse, ErrorResponse
from core.api.exceptions import ResourceNotFoundException, ValidationException
from core.api.utils import StandardPagination
from apps.users.models import Users
from .serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer


class UserListCreateView(APIView):
    """List all users or create a new user"""
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    
    def get(self, request):
        """GET /api/users/"""
        # Get query parameters
        search = request.query_params.get('search', '')
        is_active = request.query_params.get('is_active', None)
        
        # Build queryset
        queryset = Users.objects.all()
        
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) | 
                Q(email__icontains=search) |
                Q(name__icontains=search)
            )
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Paginate
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        
        # Serialize
        serializer = UserSerializer(paginated_queryset, many=True)
        
        # Return paginated response
        return paginator.get_paginated_response(serializer.data)
    
    def post(self, request):
        """POST /api/users/"""
        # Validate input
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check for duplicates
        if Users.objects.filter(username=serializer.validated_data['username']).exists():
            raise ValidationException("Username already exists")
        
        if Users.objects.filter(email=serializer.validated_data['email']).exists():
            raise ValidationException("Email already exists")
        
        # Create user
        with transaction.atomic():
            user = serializer.save(created_by=request.user)
        
        # Return success response
        response_serializer = UserSerializer(user)
        return SuccessResponse.create(
            data=response_serializer.data,
            message="User created successfully",
            resource_id=user.id
        )


class UserDetailView(APIView):
    """Retrieve, update or delete a user"""
    permission_classes = [IsAuthenticated]
    
    def get_object(self, user_id):
        """Get user or raise exception"""
        try:
            return Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            raise ResourceNotFoundException(
                resource_type="User",
                resource_id=user_id
            )
    
    def get(self, request, user_id):
        """GET /api/users/{id}/"""
        user = self.get_object(user_id)
        serializer = UserSerializer(user)
        return SuccessResponse.retrieve(
            data=serializer.data,
            message="User retrieved successfully"
        )
    
    def put(self, request, user_id):
        """PUT /api/users/{id}/"""
        user = self.get_object(user_id)
        
        # Validate input
        serializer = UserUpdateSerializer(user, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        
        # Update user
        with transaction.atomic():
            updated_user = serializer.save(last_modified_by=request.user)
        
        # Return success response
        response_serializer = UserSerializer(updated_user)
        return SuccessResponse.update(
            data=response_serializer.data,
            message="User updated successfully"
        )
    
    def patch(self, request, user_id):
        """PATCH /api/users/{id}/"""
        user = self.get_object(user_id)
        
        # Validate input
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        # Update user
        with transaction.atomic():
            updated_user = serializer.save(last_modified_by=request.user)
        
        # Return success response
        response_serializer = UserSerializer(updated_user)
        return SuccessResponse.update(
            data=response_serializer.data,
            message="User updated successfully"
        )
    
    def delete(self, request, user_id):
        """DELETE /api/users/{id}/"""
        user = self.get_object(user_id)
        
        # Soft delete (set is_active to False)
        user.is_active = False
        user.last_modified_by = request.user
        user.save()
        
        return SuccessResponse.delete(
            message="User deleted successfully"
        )
```

### serializers.py

```python
from rest_framework import serializers
from core.api.serializers import BaseModelSerializer, AuditedSerializer
from apps.users.models import Users, Profile, UserRole


class UserSerializer(BaseModelSerializer, AuditedSerializer):
    """Serializer for User responses"""
    profile_name = serializers.CharField(source='profile.name', read_only=True)
    role_name = serializers.CharField(source='user_role.name', read_only=True)
    manager_name = serializers.CharField(source='manager.name', read_only=True)
    
    class Meta:
        model = Users
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'name',
            'is_active', 'is_staff', 'profile', 'profile_name',
            'user_role', 'role_name', 'manager', 'manager_name',
            'created_date', 'created_by', 'last_modified_date', 'last_modified_by'
        ]


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating users"""
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = Users
        fields = [
            'username', 'email', 'password', 'first_name', 'last_name',
            'profile', 'user_role', 'manager'
        ]
    
    def validate_username(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters")
        return value
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Users(**validated_data)
        user.name = f"{validated_data['first_name']} {validated_data['last_name']}"
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating users"""
    
    class Meta:
        model = Users
        fields = [
            'email', 'first_name', 'last_name',
            'is_active', 'profile', 'user_role', 'manager'
        ]
```

### urls.py

```python
from django.urls import path
from .views import UserListCreateView, UserDetailView

app_name = 'users'

urlpatterns = [
    path('', UserListCreateView.as_view(), name='user-list-create'),
    path('<str:user_id>/', UserDetailView.as_view(), name='user-detail'),
]
```

---

## Example 2: Account Management API

### views.py

```python
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from core.api.responses import SuccessResponse
from core.api.exceptions import ResourceNotFoundException
from apps.accounts.models import Account
from .serializers import AccountSerializer, AccountCreateSerializer


class AccountListView(APIView):
    """List all accounts"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """GET /api/accounts/"""
        # Filter by owner if specified
        owner_id = request.query_params.get('owner_id')
        
        queryset = Account.objects.select_related('owner').all()
        
        if owner_id:
            queryset = queryset.filter(owner_id=owner_id)
        
        serializer = AccountSerializer(queryset, many=True)
        return SuccessResponse.list(
            data=serializer.data,
            message=f"{len(serializer.data)} accounts retrieved"
        )
    
    def post(self, request):
        """POST /api/accounts/"""
        serializer = AccountCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        account = serializer.save(
            owner=request.user,
            last_modified_by=request.user
        )
        
        response_serializer = AccountSerializer(account)
        return SuccessResponse.create(
            data=response_serializer.data,
            message="Account created successfully",
            resource_id=account.id
        )


class AccountDetailView(APIView):
    """Account detail operations"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, account_id):
        """GET /api/accounts/{id}/"""
        try:
            account = Account.objects.select_related(
                'owner', 'last_modified_by'
            ).prefetch_related(
                'plans', 'invoices', 'frame_agreements'
            ).get(id=account_id)
        except Account.DoesNotExist:
            raise ResourceNotFoundException("Account", account_id)
        
        serializer = AccountSerializer(account)
        return SuccessResponse.retrieve(
            data=serializer.data
        )
```

---

## Example 3: Invoice API with Validation

### views.py

```python
from rest_framework.views import APIView
from decimal import Decimal

from core.api.responses import SuccessResponse
from core.api.exceptions import ValidationException, ResourceNotFoundException
from apps.invoices.models import Invoice, InvoiceLineItem


class InvoiceCreateView(APIView):
    """Create invoice with line items"""
    
    def post(self, request):
        """POST /api/invoices/"""
        data = request.data
        
        # Validate account exists
        account_id = data.get('account_id')
        if not Account.objects.filter(id=account_id).exists():
            raise ResourceNotFoundException("Account", account_id)
        
        # Validate line items
        line_items = data.get('line_items', [])
        if not line_items:
            raise ValidationException("At least one line item is required")
        
        # Calculate totals
        net_price = Decimal('0.00')
        total_vat = Decimal('0.00')
        
        for item in line_items:
            item_net = Decimal(str(item.get('net_price', 0)))
            item_vat = Decimal(str(item.get('vat', 0)))
            net_price += item_net
            total_vat += item_vat
        
        # Create invoice
        with transaction.atomic():
            invoice = Invoice.objects.create(
                invoice_number=data['invoice_number'],
                account_id=account_id,
                invoice_date=data['invoice_date'],
                invoice_type=data['invoice_type'],
                status='Draft',
                net_price=net_price,
                total_vat=total_vat,
                total_invoice_value=net_price + total_vat,
                created_by=request.user,
                last_modified_by=request.user
            )
            
            # Create line items
            for item_data in line_items:
                InvoiceLineItem.objects.create(
                    invoice=invoice,
                    product_id=item_data['product_id'],
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price'],
                    net_price=item_data['net_price'],
                    vat=item_data.get('vat', 0),
                    unique_line_code=item_data['unique_line_code'],
                    status='Active',
                    created_by=request.user
                )
        
        # Return response
        serializer = InvoiceSerializer(invoice)
        return SuccessResponse.create(
            data=serializer.data,
            message="Invoice created successfully",
            resource_id=invoice.id
        )
```

---

## Example 4: Authentication API

### views.py

```python
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from core.api.responses import SuccessResponse
from core.api.exceptions import InvalidCredentialsException


class LoginView(APIView):
    """User login"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """POST /api/auth/login/"""
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            raise InvalidCredentialsException("Username and password required")
        
        user = authenticate(username=username, password=password)
        
        if not user:
            raise InvalidCredentialsException("Invalid credentials")
        
        if not user.is_active:
            raise InvalidCredentialsException("Account is inactive")
        
        # Generate token (use JWT or similar)
        # token = generate_token(user)
        
        return SuccessResponse.login(
            data={
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "name": user.name
                },
                # "token": token
            },
            message="Login successful"
        )
```

---

## Example 5: Bulk Operations

### views.py

```python
from rest_framework.views import APIView
from core.api.responses import SuccessResponse
from core.api.serializers import IDListRequestSerializer
from apps.users.models import Users


class BulkUserActivateView(APIView):
    """Bulk activate users"""
    
    def post(self, request):
        """POST /api/users/bulk-activate/"""
        # Validate input
        serializer = IDListRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_ids = serializer.validated_data['ids']
        
        # Update users
        updated_count = Users.objects.filter(
            id__in=user_ids
        ).update(
            is_active=True,
            last_modified_by=request.user
        )
        
        return SuccessResponse.custom(
            data={
                "updated_count": updated_count,
                "user_ids": user_ids
            },
            message=f"{updated_count} users activated successfully"
        )
```

---

## Testing Examples

```python
from django.test import TestCase
from rest_framework.test import APIClient
from apps.users.models import Users


class UserAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = Users.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_list_users(self):
        """Test GET /api/users/"""
        response = self.client.get('/api/users/')
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        self.assertIn('meta', response.data)
    
    def test_create_user(self):
        """Test POST /api/users/"""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = self.client.post('/api/users/', data)
        
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data['success'])
        self.assertIn('resource_id', response.data.get('meta', {}))
    
    def test_get_user_not_found(self):
        """Test GET /api/users/{invalid_id}/"""
        response = self.client.get('/api/users/INVALID_ID/')
        
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['error_code'], 'RESOURCE_NOT_FOUND')
```

---

These examples demonstrate the complete usage of the standardized API response system in a real-world Django REST Framework application.
