# Sales Analytics API Documentation

## Overview

The Sales Analytics API provides a 4-level drilldown reporting system for sales order analysis with RFC (Rolling Forecast) comparison. Each level provides progressively more detailed insights into sales performance.

## Architecture

- Separate API endpoints per level (no dynamic level-based API)
- Controller → Service → Repository pattern
- Raw SQL queries in service layer for optimal performance
- Standardized response format with pagination
- Parameter binding for security

## Common Features

### Mandatory Filters (All APIs)

All endpoints require:
- `accountId`: Salesforce Account ID
- `from`: Start month in YYYY-MM format
- `to`: End month in YYYY-MM format

### Date Conversion

The system automatically converts month ranges:
- `from` → First day of month (e.g., 2025-01 → 2025-01-01)
- `to` → Last day of month (e.g., 2025-12 → 2025-12-31)

All queries use `orders.ord_effective_date` for date filtering.

### Pagination

All endpoints support pagination:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

### Response Format

```json
{
  "success": true,
  "message": "Data retrieved successfully",
  "data": [...],
  "meta": {
    "pagination": {
      "current_page": 1,
      "page_size": 20,
      "total_count": 45,
      "total_pages": 3,
      "has_next": true,
      "has_previous": false
    }
  }
}
```

---

## Level 1: Product Family Analytics

### Endpoint

```
GET /api/sales/family
```

### Description

Provides aggregated sales analytics at the product family level, comparing actual sales, last year sales, and RFC (Rolling Forecast).

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| accountId | string | Yes | Salesforce Account ID |
| from | string | Yes | Start month (YYYY-MM) |
| to | string | Yes | End month (YYYY-MM) |
| page | integer | No | Page number (default: 1) |
| page_size | integer | No | Items per page (default: 20, max: 100) |

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| family | string | Product family name |
| actualSales | decimal | Sum of ordered amounts in current period |
| openSales | decimal | Sum of open amounts in current period |
| lastYearSales | decimal | Sum of ordered amounts in same period last year |
| rfc | decimal | Sum of approved forecast values |
| deviationPercent | decimal | ((actualSales - rfc) / rfc) * 100 |

### Calculation Logic

#### Actuals CTE
```sql
SELECT
    prd.prd_family,
    SUM(ori.ori_ordered_amount) AS actualSales,
    SUM(ori.ori_open_amount) AS openSales
FROM products prd
LEFT JOIN order_line_items ori ON ori.ori_product_id = prd.prd_sf_id
LEFT JOIN orders ord ON ord.ord_sf_id = ori.ori_order_id
WHERE
    ord.ord_account_id = :accountId
    AND ord.ord_effective_date BETWEEN :fromDate AND :toDate
    AND ord.ord_active = 1
    AND ori.ori_active = 1
    AND prd.prd_active = 1
GROUP BY prd.prd_family
```

#### Last Year CTE
Same query with date range shifted back 1 year.

#### RFC CTE
```sql
SELECT
    prd.prd_family,
    SUM(arf.arf_approved_value) AS rfc
FROM arf_rolling_forecasts arf
JOIN products prd ON prd.prd_sf_id = arf.arf_product_id
WHERE
    arf.arf_account_id = :accountId
    AND arf.arf_status = 'Approved'
    AND arf.arf_forecast_date BETWEEN :fromDate AND :toDate
    AND arf.arf_active = 1
    AND prd.prd_active = 1
GROUP BY prd.prd_family
```

### Example Request

```bash
GET /api/sales/family?accountId=0011234567890ABC&from=2025-01&to=2025-12&page=1&page_size=20
```

### Example Response

```json
{
  "success": true,
  "message": "Product family analytics retrieved successfully",
  "data": [
    {
      "family": "Electronics",
      "actualSales": 125000.50,
      "openSales": 15000.00,
      "lastYearSales": 110000.00,
      "rfc": 120000.00,
      "deviationPercent": 4.17
    },
    {
      "family": "Furniture",
      "actualSales": 85000.00,
      "openSales": 8500.00,
      "lastYearSales": 90000.00,
      "rfc": 95000.00,
      "deviationPercent": -10.53
    }
  ],
  "meta": {
    "pagination": {
      "current_page": 1,
      "page_size": 20,
      "total_count": 2,
      "total_pages": 1,
      "has_next": false,
      "has_previous": false
    }
  }
}
```

---

## Level 2: Product Analytics

### Endpoint

```
GET /api/sales/product
```

### Description

Provides detailed sales analytics for individual products within a specific product family.

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| accountId | string | Yes | Salesforce Account ID |
| family | string | Yes | Product family name |
| from | string | Yes | Start month (YYYY-MM) |
| to | string | Yes | End month (YYYY-MM) |
| page | integer | No | Page number (default: 1) |
| page_size | integer | No | Items per page (default: 20, max: 100) |

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| productId | string | Product Salesforce ID |
| productName | string | Product name |
| actualSales | decimal | Sum of ordered amounts in current period |
| openSales | decimal | Sum of open amounts in current period |
| lastYearSales | decimal | Sum of ordered amounts in same period last year |
| rfc | decimal | Sum of approved forecast values |
| deviationPercent | decimal | ((actualSales - rfc) / rfc) * 100 |

### Calculation Logic

Same as Level 1, but:
- Filtered by `prd.prd_family = :familyName`
- Grouped by `ori.ori_product_id` and `prd.prd_name`
- RFC grouped by `arf.arf_product_id`

### Example Request

```bash
GET /api/sales/product?accountId=0011234567890ABC&family=Electronics&from=2025-01&to=2025-12&page=1&page_size=20
```

### Example Response

```json
{
  "success": true,
  "message": "Product analytics retrieved successfully",
  "data": [
    {
      "productId": "01t1234567890ABC",
      "productName": "Laptop Pro 15",
      "actualSales": 75000.00,
      "openSales": 10000.00,
      "lastYearSales": 65000.00,
      "rfc": 70000.00,
      "deviationPercent": 7.14
    },
    {
      "productId": "01t1234567890DEF",
      "productName": "Tablet Ultra",
      "actualSales": 50000.50,
      "openSales": 5000.00,
      "lastYearSales": 45000.00,
      "rfc": 50000.00,
      "deviationPercent": 0.10
    }
  ],
  "meta": {
    "pagination": {
      "current_page": 1,
      "page_size": 20,
      "total_count": 2,
      "total_pages": 1,
      "has_next": false,
      "has_previous": false
    }
  }
}
```

---

## Level 3: Order Contribution

### Endpoint

```
GET /api/sales/orders
```

### Description

Shows how a specific product contributed to each order. Only displays the selected product's contribution per order.

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| accountId | string | Yes | Salesforce Account ID |
| productId | string | Yes | Product Salesforce ID |
| from | string | Yes | Start month (YYYY-MM) |
| to | string | Yes | End month (YYYY-MM) |
| page | integer | No | Page number (default: 1) |
| page_size | integer | No | Items per page (default: 20, max: 100) |

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| orderId | string | Order Salesforce ID |
| orderNumber | string | Order number |
| orderStatus | string | Order status |
| orderedQuantity | decimal | Total ordered quantity for this product |
| orderedAmount | decimal | Total ordered amount for this product |
| openQuantity | decimal | Open quantity for this product |
| openAmount | decimal | Open amount for this product |

### Calculation Logic

```sql
SELECT
    ori.ori_order_id,
    ord.ord_order_number,
    ord.ord_status,
    SUM(ori.ori_ordered_quantity) AS orderedQuantity,
    SUM(ori.ori_ordered_amount) AS orderedAmount,
    SUM(ori.ori_open_quantity) AS openQuantity,
    SUM(ori.ori_open_amount) AS openAmount
FROM order_line_items ori
JOIN orders ord ON ord.ord_sf_id = ori.ori_order_id
WHERE
    ord.ord_account_id = :accountId
    AND ori.ori_product_id = :productId
    AND ord.ord_effective_date BETWEEN :fromDate AND :toDate
    AND ord.ord_active = 1
    AND ori.ori_active = 1
GROUP BY ori.ori_order_id, ord.ord_order_number, ord.ord_status
```

### Example Request

```bash
GET /api/sales/orders?accountId=0011234567890ABC&productId=01t1234567890ABC&from=2025-01&to=2025-12&page=1&page_size=20
```

### Example Response

```json
{
  "success": true,
  "message": "Order contribution data retrieved successfully",
  "data": [
    {
      "orderId": "8011234567890ABC",
      "orderNumber": "ORD-2025-001",
      "orderStatus": "Activated",
      "orderedQuantity": 10.00,
      "orderedAmount": 15000.00,
      "openQuantity": 2.00,
      "openAmount": 3000.00
    },
    {
      "orderId": "8011234567890DEF",
      "orderNumber": "ORD-2025-002",
      "orderStatus": "Draft",
      "orderedQuantity": 5.00,
      "orderedAmount": 7500.00,
      "openQuantity": 5.00,
      "openAmount": 7500.00
    }
  ],
  "meta": {
    "pagination": {
      "current_page": 1,
      "page_size": 20,
      "total_count": 2,
      "total_pages": 1,
      "has_next": false,
      "has_previous": false
    }
  }
}
```

---

## Level 4: Order Details

### Endpoint

```
GET /api/sales/order-details
```

### Description

Shows ALL products inside a specific order with their quantities and amounts.

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| accountId | string | Yes | Salesforce Account ID |
| orderId | string | Yes | Order Salesforce ID |
| from | string | Yes | Start month (YYYY-MM) |
| to | string | Yes | End month (YYYY-MM) |
| page | integer | No | Page number (default: 1) |
| page_size | integer | No | Items per page (default: 20, max: 100) |

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| productId | string | Product Salesforce ID |
| productName | string | Product name |
| status | string | Line item status |
| orderedQuantity | decimal | Total ordered quantity |
| orderedAmount | decimal | Total ordered amount |
| openQuantity | decimal | Open quantity |
| openAmount | decimal | Open amount |

### Calculation Logic

```sql
SELECT
    ori.ori_product_id,
    prd.prd_name,
    ori.ori_status,
    SUM(ori.ori_ordered_quantity) AS orderedQuantity,
    SUM(ori.ori_ordered_amount) AS orderedAmount,
    SUM(ori.ori_open_quantity) AS openQuantity,
    SUM(ori.ori_open_amount) AS openAmount
FROM order_line_items ori
JOIN orders ord ON ord.ord_sf_id = ori.ori_order_id
JOIN products prd ON prd.prd_sf_id = ori.ori_product_id
WHERE
    ord.ord_account_id = :accountId
    AND ori.ori_order_id = :orderId
    AND ord.ord_effective_date BETWEEN :fromDate AND :toDate
    AND ord.ord_active = 1
    AND ori.ori_active = 1
    AND prd.prd_active = 1
GROUP BY ori.ori_product_id, prd.prd_name, ori.ori_status
```

### Example Request

```bash
GET /api/sales/order-details?accountId=0011234567890ABC&orderId=8011234567890ABC&from=2025-01&to=2025-12&page=1&page_size=20
```

### Example Response

```json
{
  "success": true,
  "message": "Order details retrieved successfully",
  "data": [
    {
      "productId": "01t1234567890ABC",
      "productName": "Laptop Pro 15",
      "status": "Activated",
      "orderedQuantity": 10.00,
      "orderedAmount": 15000.00,
      "openQuantity": 2.00,
      "openAmount": 3000.00
    },
    {
      "productId": "01t1234567890GHI",
      "productName": "Mouse Wireless",
      "status": "Activated",
      "orderedQuantity": 50.00,
      "orderedAmount": 1000.00,
      "openQuantity": 0.00,
      "openAmount": 0.00
    },
    {
      "productId": "01t1234567890JKL",
      "productName": "Keyboard Mechanical",
      "status": "Activated",
      "orderedQuantity": 20.00,
      "orderedAmount": 2000.00,
      "openQuantity": 5.00,
      "openAmount": 500.00
    }
  ],
  "meta": {
    "pagination": {
      "current_page": 1,
      "page_size": 20,
      "total_count": 3,
      "total_pages": 1,
      "has_next": false,
      "has_previous": false
    }
  }
}
```

---

## Error Responses

### Validation Error

```json
{
  "success": false,
  "message": "Invalid query parameters",
  "errors": [
    {
      "field": "accountId",
      "message": "accountId parameter is required"
    }
  ]
}
```

### Date Format Error

```json
{
  "success": false,
  "message": "Invalid date format",
  "errors": [
    {
      "field": "from/to",
      "message": "Invalid date format. Expected YYYY-MM"
    }
  ]
}
```

### Server Error

```json
{
  "success": false,
  "message": "An error occurred while retrieving analytics data",
  "error_code": "ANALYTICS_CALCULATION_ERROR"
}
```

---

## Database Indexes

The following indexes are automatically created by migration to optimize query performance:

### Orders Table
- `idx_orders_account` on `ord_account_id`
- `idx_orders_effective_date` on `ord_effective_date`

### Order Line Items Table
- `idx_order_line_items_product` on `ori_product_id`
- `idx_order_line_items_order` on `ori_order_id`

### Products Table
- `idx_products_sf_id` on `prd_sf_id`
- `idx_products_family` on `prd_family`

### ARF Rolling Forecasts Table
- `idx_arf_account` on `arf_account_id`
- `idx_arf_product` on `arf_product_id`
- `idx_arf_forecast_date` on `arf_forecast_date`

---

## Implementation Details

### Architecture Pattern

```
Controller (analytics_views.py)
    ↓
Service Layer (analytics_services.py)
    ↓
Repository (Raw SQL with parameter binding)
```

### Security Features

- Parameter binding to prevent SQL injection
- Input validation for all parameters
- Date range validation
- Pagination limits (max 100 items per page)

### Performance Optimizations

- CTE (Common Table Expressions) for complex queries
- Database indexes on frequently queried columns
- Efficient JOIN operations
- Aggregation at database level

### Code Standards

- Type hints for all methods
- Comprehensive docstrings
- Error handling with specific error codes
- Standardized response format
- Pagination support on all endpoints

---

## Usage Examples

### Python Requests

```python
import requests

base_url = "http://localhost:8000/api/sales"
params = {
    "accountId": "0011234567890ABC",
    "from": "2025-01",
    "to": "2025-12",
    "page": 1,
    "page_size": 20
}

# Level 1: Product Family
response = requests.get(f"{base_url}/family", params=params)
families = response.json()

# Level 2: Products in a family
params["family"] = "Electronics"
response = requests.get(f"{base_url}/product", params=params)
products = response.json()

# Level 3: Order contribution for a product
params["productId"] = "01t1234567890ABC"
del params["family"]
response = requests.get(f"{base_url}/orders", params=params)
orders = response.json()

# Level 4: Order details
params["orderId"] = "8011234567890ABC"
del params["productId"]
response = requests.get(f"{base_url}/order-details", params=params)
details = response.json()
```

### cURL

```bash
# Level 1: Product Family
curl -X GET "http://localhost:8000/api/sales/family?accountId=0011234567890ABC&from=2025-01&to=2025-12&page=1&page_size=20"

# Level 2: Products
curl -X GET "http://localhost:8000/api/sales/product?accountId=0011234567890ABC&family=Electronics&from=2025-01&to=2025-12&page=1&page_size=20"

# Level 3: Order Contribution
curl -X GET "http://localhost:8000/api/sales/orders?accountId=0011234567890ABC&productId=01t1234567890ABC&from=2025-01&to=2025-12&page=1&page_size=20"

# Level 4: Order Details
curl -X GET "http://localhost:8000/api/sales/order-details?accountId=0011234567890ABC&orderId=8011234567890ABC&from=2025-01&to=2025-12&page=1&page_size=20"
```

---

## Testing

### Manual Testing

1. Start the development server:
```bash
python manage.py runserver
```

2. Access Swagger UI:
```
http://localhost:8000/api/schema/swagger-ui/
```

3. Test each endpoint with sample data

### Validation Checklist

- [ ] All required parameters validated
- [ ] Date format validation (YYYY-MM)
- [ ] Date range validation (from <= to)
- [ ] Pagination working correctly
- [ ] Empty results return empty array
- [ ] Error responses follow standard format
- [ ] All indexes created successfully
- [ ] Query performance acceptable

---

## Maintenance

### Adding New Filters

To add additional filters to any endpoint:

1. Update the view to accept new query parameter
2. Add validation in the view
3. Pass parameter to service method
4. Update SQL query in service layer
5. Update API documentation

### Performance Monitoring

Monitor these metrics:
- Query execution time
- Database connection pool usage
- API response time
- Memory usage during aggregation

### Troubleshooting

**Slow queries:**
- Check if indexes are created
- Analyze query execution plan
- Consider adding composite indexes

**Empty results:**
- Verify date range is correct
- Check account ID exists
- Ensure active flags are set correctly

**Pagination issues:**
- Verify page and page_size parameters
- Check total_count calculation
- Ensure consistent ordering

---

## API Endpoints Summary

| Level | Endpoint | Purpose |
|-------|----------|---------|
| 1 | `/api/sales/family` | Product family analytics |
| 2 | `/api/sales/product` | Product analytics by family |
| 3 | `/api/sales/orders` | Order contribution by product |
| 4 | `/api/sales/order-details` | All products in an order |

All endpoints support pagination and follow the same response format.
