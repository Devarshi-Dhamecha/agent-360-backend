# Database Schema Guide

## PostgreSQL Setup

### Connection Details

```
Engine: PostgreSQL
Host: localhost
Port: 5432
Database: agent360_db
User: postgres
```

### Create Database

```sql
CREATE DATABASE agent360_db;
CREATE USER agent360_user WITH PASSWORD 'secure_password';
ALTER ROLE agent360_user SET client_encoding TO 'utf8';
ALTER ROLE agent360_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE agent360_user SET default_transaction_deferrable TO on;
ALTER ROLE agent360_user SET default_transaction_read_committed TO on;
GRANT ALL PRIVILEGES ON DATABASE agent360_db TO agent360_user;
```

## Schema Design Principles

### 1. Naming Conventions

- **Tables**: Plural, snake_case (e.g., `products`, `user_profiles`)
- **Columns**: snake_case (e.g., `created_at`, `is_active`)
- **Primary Keys**: `id` (auto-incrementing)
- **Foreign Keys**: `{table_name}_id` (e.g., `product_id`, `user_id`)
- **Indexes**: `idx_{table}_{column}` (e.g., `idx_products_name`)
- **Constraints**: `ck_{table}_{constraint}` (e.g., `ck_products_price_positive`)

### 2. Data Types

| Type | Usage |
|------|-------|
| BIGINT | Primary keys, large numbers |
| INTEGER | Regular integers |
| DECIMAL(10,2) | Money, precise decimals |
| VARCHAR(255) | Short text |
| TEXT | Long text |
| BOOLEAN | True/False values |
| TIMESTAMP | Date and time |
| DATE | Date only |
| UUID | Unique identifiers |
| JSON/JSONB | Structured data |

### 3. Common Fields

Every table should have:

```sql
id BIGINT PRIMARY KEY AUTO_INCREMENT,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
is_active BOOLEAN DEFAULT TRUE
```

## Example Schema

### Users Table

```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_staff BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT ck_users_email_format CHECK (email LIKE '%@%.%'),
    INDEX idx_users_email (email),
    INDEX idx_users_username (username),
    INDEX idx_users_created_at (created_at)
);
```

### Products Table

```sql
CREATE TABLE products (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock INTEGER DEFAULT 0,
    category_id BIGINT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT ck_products_price_positive CHECK (price >= 0),
    CONSTRAINT ck_products_stock_positive CHECK (stock >= 0),
    CONSTRAINT fk_products_category FOREIGN KEY (category_id) 
        REFERENCES categories(id) ON DELETE SET NULL,
    
    INDEX idx_products_name (name),
    INDEX idx_products_category_id (category_id),
    INDEX idx_products_is_active (is_active),
    INDEX idx_products_created_at (created_at)
);
```

### Categories Table

```sql
CREATE TABLE categories (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    slug VARCHAR(255) UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_categories_slug (slug),
    INDEX idx_categories_name (name)
);
```

### Orders Table

```sql
CREATE TABLE orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    payment_method VARCHAR(50),
    shipping_address TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT ck_orders_total_positive CHECK (total_amount >= 0),
    CONSTRAINT fk_orders_user FOREIGN KEY (user_id) 
        REFERENCES users(id) ON DELETE CASCADE,
    
    INDEX idx_orders_user_id (user_id),
    INDEX idx_orders_status (status),
    INDEX idx_orders_created_at (created_at),
    INDEX idx_orders_order_number (order_number)
);
```

### Order Items Table

```sql
CREATE TABLE order_items (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT ck_order_items_quantity CHECK (quantity > 0),
    CONSTRAINT ck_order_items_price CHECK (unit_price >= 0),
    CONSTRAINT fk_order_items_order FOREIGN KEY (order_id) 
        REFERENCES orders(id) ON DELETE CASCADE,
    CONSTRAINT fk_order_items_product FOREIGN KEY (product_id) 
        REFERENCES products(id) ON DELETE RESTRICT,
    
    INDEX idx_order_items_order_id (order_id),
    INDEX idx_order_items_product_id (product_id)
);
```

## Relationships

### One-to-Many

```
User (1) ──── (Many) Orders
```

```sql
ALTER TABLE orders ADD CONSTRAINT fk_orders_user 
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
```

### Many-to-Many

```
Products (Many) ──── (Many) Categories
```

```sql
CREATE TABLE product_categories (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    product_id BIGINT NOT NULL,
    category_id BIGINT NOT NULL,
    
    CONSTRAINT fk_pc_product FOREIGN KEY (product_id) 
        REFERENCES products(id) ON DELETE CASCADE,
    CONSTRAINT fk_pc_category FOREIGN KEY (category_id) 
        REFERENCES categories(id) ON DELETE CASCADE,
    
    UNIQUE KEY unique_product_category (product_id, category_id),
    INDEX idx_pc_category_id (category_id)
);
```

## Indexes

### Index Strategy

```sql
-- Single column index
CREATE INDEX idx_products_name ON products(name);

-- Composite index (for queries filtering by multiple columns)
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- Partial index (for filtered queries)
CREATE INDEX idx_products_active ON products(id) WHERE is_active = TRUE;

-- Full-text search index
CREATE FULLTEXT INDEX idx_products_search ON products(name, description);
```

### Query Performance

```sql
-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM products WHERE name LIKE '%laptop%';

-- Check index usage
SELECT * FROM pg_stat_user_indexes;
```

## Constraints

### Primary Key

```sql
ALTER TABLE products ADD PRIMARY KEY (id);
```

### Unique Constraint

```sql
ALTER TABLE users ADD CONSTRAINT unique_email UNIQUE (email);
```

### Check Constraint

```sql
ALTER TABLE products ADD CONSTRAINT ck_price_positive CHECK (price > 0);
```

### Foreign Key

```sql
ALTER TABLE orders ADD CONSTRAINT fk_orders_user 
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
```

## Migrations

### Create Migration

```bash
python manage.py makemigrations apps.products
```

### Migration File Example

```python
# apps/products/migrations/0001_initial.py
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    
    dependencies = []
    
    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('stock', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
```

### Apply Migrations

```bash
python manage.py migrate
```

## Backup & Restore

### Backup Database

```bash
pg_dump -U postgres -h localhost agent360_db > backup.sql
```

### Restore Database

```bash
psql -U postgres -h localhost agent360_db < backup.sql
```

### Django Dump/Load

```bash
# Dump data
python manage.py dumpdata > data.json

# Load data
python manage.py loaddata data.json
```

## Performance Optimization

### Query Optimization

```python
# ❌ Bad: N+1 queries
products = Product.objects.all()
for product in products:
    print(product.category.name)

# ✅ Good: Use select_related
products = Product.objects.select_related('category').all()

# ✅ Good: Use prefetch_related
categories = Category.objects.prefetch_related('products').all()

# ✅ Good: Use only()
products = Product.objects.only('id', 'name', 'price')

# ✅ Good: Use values()
products = Product.objects.values('id', 'name', 'price')
```

### Connection Pooling

```python
# config/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'CONN_MAX_AGE': 600,  # Connection pooling
        'ATOMIC_REQUESTS': True,
    }
}
```

## Monitoring

### Check Database Size

```sql
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Check Slow Queries

```sql
SELECT query, calls, mean_time, max_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

### Monitor Connections

```sql
SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;
```

## Best Practices

1. **Always use transactions** for data consistency
2. **Add indexes** for frequently queried columns
3. **Use constraints** to maintain data integrity
4. **Normalize data** to reduce redundancy
5. **Archive old data** to maintain performance
6. **Regular backups** for disaster recovery
7. **Monitor performance** regularly
8. **Use connection pooling** in production
9. **Document schema changes** in migrations
10. **Test migrations** before production deployment
