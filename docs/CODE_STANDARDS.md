# Code Standards & Best Practices

## Python Code Style

### PEP 8 Compliance
- Line length: 88 characters (Black formatter standard)
- Use 4 spaces for indentation
- Two blank lines between top-level definitions
- One blank line between method definitions

### Naming Conventions

```python
# Constants
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30

# Functions and variables
def calculate_total_price(items):
    total_amount = 0
    return total_amount

# Classes
class UserSerializer:
    pass

class ProductListView:
    pass

# Private methods/attributes
def _internal_helper():
    pass

_private_variable = "internal"
```

### Type Hints
Always use type hints for better code clarity:

```python
from typing import Optional, List, Dict
from django.db.models import QuerySet

def get_user_by_email(email: str) -> Optional['User']:
    """Get user by email address."""
    return User.objects.filter(email=email).first()

def process_items(items: List[Dict[str, any]]) -> QuerySet:
    """Process a list of items."""
    pass
```

### Docstrings
Use Google-style docstrings:

```python
def calculate_discount(price: float, discount_percent: float) -> float:
    """
    Calculate discounted price.
    
    Args:
        price: Original price in dollars
        discount_percent: Discount percentage (0-100)
    
    Returns:
        Discounted price
    
    Raises:
        ValueError: If discount_percent is not between 0-100
    """
    if not 0 <= discount_percent <= 100:
        raise ValueError("Discount must be between 0-100")
    return price * (1 - discount_percent / 100)
```

## Django Models

### Model Definition Standards

```python
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

class BaseModel(models.Model):
    """Abstract base model with common fields."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class Product(BaseModel):
    """Product model for e-commerce."""
    
    name = models.CharField(
        max_length=255,
        help_text="Product name"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed product description"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Product price in USD"
    )
    stock = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Available stock quantity"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether product is available for sale"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active', '-created_at']),
        ]
        verbose_name = "Product"
        verbose_name_plural = "Products"
    
    def __str__(self) -> str:
        return self.name
    
    def is_in_stock(self) -> bool:
        """Check if product is in stock."""
        return self.stock > 0
```

### Model Best Practices

- Always define `__str__()` method
- Use `help_text` for all fields
- Define `Meta` class with `ordering`, `indexes`, `verbose_name`
- Use abstract base models for common fields
- Add methods for business logic
- Use `validators` for field validation

## Views & Serializers

### Function-Based Views

```python
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

@require_http_methods(["GET", "POST"])
def product_list(request):
    """
    Handle product list retrieval and creation.
    
    GET: Return list of products
    POST: Create new product
    """
    if request.method == "GET":
        products = Product.objects.filter(is_active=True)
        serializer = ProductSerializer(products, many=True)
        return JsonResponse({"data": serializer.data})
    
    elif request.method == "POST":
        serializer = ProductSerializer(data=request.POST)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)
```

### Serializers

```python
from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model."""
    
    is_in_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'price',
            'stock',
            'is_active',
            'is_in_stock',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_is_in_stock(self, obj: Product) -> bool:
        """Get stock status."""
        return obj.is_in_stock()
    
    def validate_price(self, value: float) -> float:
        """Validate price is positive."""
        if value <= 0:
            raise serializers.ValidationError("Price must be positive")
        return value
```

## Services Layer

Create a `services.py` file for business logic:

```python
from typing import Optional, List
from django.db.models import QuerySet
from .models import Product

class ProductService:
    """Service layer for product operations."""
    
    @staticmethod
    def get_active_products() -> QuerySet:
        """Get all active products."""
        return Product.objects.filter(is_active=True)
    
    @staticmethod
    def get_in_stock_products() -> QuerySet:
        """Get products that are in stock."""
        return Product.objects.filter(is_active=True, stock__gt=0)
    
    @staticmethod
    def create_product(
        name: str,
        price: float,
        description: str = "",
        stock: int = 0
    ) -> Product:
        """Create a new product."""
        product = Product.objects.create(
            name=name,
            price=price,
            description=description,
            stock=stock
        )
        return product
    
    @staticmethod
    def update_stock(product_id: int, quantity: int) -> Optional[Product]:
        """Update product stock."""
        try:
            product = Product.objects.get(id=product_id)
            product.stock = max(0, product.stock + quantity)
            product.save()
            return product
        except Product.DoesNotExist:
            return None
```

## Error Handling

### Custom Exceptions

```python
# apps/products/exceptions.py
class ProductException(Exception):
    """Base exception for product operations."""
    pass

class ProductNotFound(ProductException):
    """Raised when product is not found."""
    pass

class InsufficientStock(ProductException):
    """Raised when product stock is insufficient."""
    pass
```

### Exception Usage

```python
from .exceptions import ProductNotFound, InsufficientStock

def purchase_product(product_id: int, quantity: int) -> bool:
    """Purchase a product."""
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        raise ProductNotFound(f"Product {product_id} not found")
    
    if product.stock < quantity:
        raise InsufficientStock(
            f"Only {product.stock} items available"
        )
    
    product.stock -= quantity
    product.save()
    return True
```

## Testing Standards

### Unit Tests

```python
from django.test import TestCase
from .models import Product
from .services import ProductService

class ProductModelTest(TestCase):
    """Test Product model."""
    
    def setUp(self):
        """Set up test data."""
        self.product = Product.objects.create(
            name="Test Product",
            price=99.99,
            stock=10
        )
    
    def test_product_creation(self):
        """Test product is created correctly."""
        self.assertEqual(self.product.name, "Test Product")
        self.assertEqual(self.product.price, 99.99)
        self.assertTrue(self.product.is_active)
    
    def test_is_in_stock(self):
        """Test stock checking."""
        self.assertTrue(self.product.is_in_stock())
        self.product.stock = 0
        self.assertFalse(self.product.is_in_stock())


class ProductServiceTest(TestCase):
    """Test ProductService."""
    
    def setUp(self):
        """Set up test data."""
        Product.objects.create(name="Product 1", price=10, stock=5)
        Product.objects.create(name="Product 2", price=20, stock=0)
    
    def test_get_in_stock_products(self):
        """Test getting in-stock products."""
        products = ProductService.get_in_stock_products()
        self.assertEqual(products.count(), 1)
```

## Logging

### Logging Standards

```python
import logging

logger = logging.getLogger(__name__)

def process_order(order_id: int) -> bool:
    """Process an order."""
    try:
        logger.info(f"Processing order {order_id}")
        order = Order.objects.get(id=order_id)
        order.status = "processing"
        order.save()
        logger.info(f"Order {order_id} processed successfully")
        return True
    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found")
        return False
    except Exception as e:
        logger.exception(f"Error processing order {order_id}: {str(e)}")
        raise
```

## URL Routing

### URL Configuration

```python
# apps/products/urls.py
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='list'),
    path('<int:product_id>/', views.product_detail, name='detail'),
    path('<int:product_id>/purchase/', views.purchase_product, name='purchase'),
]

# config/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/products/', include('apps.products.urls')),
]
```

## Database Queries

### Query Optimization

```python
# ❌ Bad: N+1 query problem
products = Product.objects.all()
for product in products:
    print(product.category.name)  # Extra query per product

# ✅ Good: Use select_related
products = Product.objects.select_related('category').all()

# ✅ Good: Use prefetch_related for reverse relations
categories = Category.objects.prefetch_related('products').all()

# ✅ Good: Use only() to limit fields
products = Product.objects.only('id', 'name', 'price')

# ✅ Good: Use values() for specific fields
products = Product.objects.values('id', 'name', 'price')
```

## Security Best Practices

1. **Never hardcode secrets** - Use environment variables
2. **Validate all inputs** - Use Django validators and serializers
3. **Use CSRF protection** - Enabled by default
4. **SQL Injection prevention** - Use ORM, never raw SQL
5. **XSS prevention** - Django templates auto-escape by default
6. **Authentication** - Use Django's built-in auth system
7. **Permissions** - Implement proper permission checks

## Code Review Checklist

- [ ] Code follows PEP 8 style guide
- [ ] Type hints are present
- [ ] Docstrings are complete
- [ ] No hardcoded values or secrets
- [ ] Error handling is implemented
- [ ] Tests are included
- [ ] Database queries are optimized
- [ ] Security best practices are followed
- [ ] No duplicate code
- [ ] Variable names are descriptive
