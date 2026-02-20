# Product Performance Variance API

## Overview

API endpoint to fetch top and bottom performing products based on deviation between approved forecast values and actual invoice revenue for a specified date range.

## Endpoint

```
GET /api/products/performance
```

## Query Parameters

| Parameter | Type | Required | Format | Description |
|-----------|------|----------|--------|-------------|
| `account_id` | string | Yes | Salesforce ID | Account ID to filter products by |
| `from` | string | Yes | YYYY-MM | Start month for analysis |
| `to` | string | Yes | YYYY-MM | End month for analysis |

### Examples

```
GET /api/products/performance?account_id=0011234567890ABC&from=2025-07&to=2025-12
GET /api/products/performance?account_id=0011234567890ABC&from=2026-02&to=2026-02
```

## Business Logic

### Actual Revenue Calculation

**Source:** `invoice_line_items.net_price`

**Joins:**
- `invoice_line_items` → `invoices` → `products`

**Filters:**
- `invoices.inv_account_id` = :account_id
- `invoices.invoice_date` BETWEEN :from_date AND :to_date
- `invoices.status` = 'Closed'
- `invoices.valid` = true
- `invoice_line_items.valid` = true
- `invoices.invoice_type` != 'Credit Note'

**Aggregation:**
```sql
actualRevenue = SUM(invoice_line_items.net_price) GROUP BY product
```

### Forecast Revenue Calculation

**Source:** `forecast.arf_approved_value`

**Filters:**
- `forecast.arf_account_id` = :account_id
- `forecast.arf_forecast_date` BETWEEN :from_date AND :to_date
- `forecast.arf_status` = 'Approved'

**Aggregation:**
```sql
forecastRevenue = SUM(forecast.arf_approved_value) GROUP BY forecast.arf_product
```

### Deviation Calculation

For each product:

```
actualRevenue = SUM(invoice_line_items.net_price)
forecastRevenue = SUM(forecast.arf_approved_value)
deviation = actualRevenue - forecastRevenue
deviationPercent = IF forecastRevenue = 0 THEN 0 ELSE (deviation / forecastRevenue) * 100
```

### Ranking Logic

**Top Performers:**
- Products with highest deviation (DESC)
- LIMIT 3

**Bottom Performers:**
- Products with lowest deviation (ASC)
- LIMIT 3

## Response Format

### Success Response (200 OK)

```json
{
  "success": true,
  "message": "Product performance data retrieved successfully",
  "data": {
    "topPerformers": [
      {
        "productId": "PRD-001",
        "productName": "Product A",
        "actualRevenue": 150000.00,
        "forecastRevenue": 100000.00,
        "deviation": 50000.00,
        "deviationPercent": 50.00
      },
      {
        "productId": "PRD-002",
        "productName": "Product B",
        "actualRevenue": 120000.00,
        "forecastRevenue": 90000.00,
        "deviation": 30000.00,
        "deviationPercent": 33.33
      },
      {
        "productId": "PRD-003",
        "productName": "Product C",
        "actualRevenue": 80000.00,
        "forecastRevenue": 60000.00,
        "deviation": 20000.00,
        "deviationPercent": 33.33
      }
    ],
    "bottomPerformers": [
      {
        "productId": "PRD-010",
        "productName": "Product J",
        "actualRevenue": 30000.00,
        "forecastRevenue": 80000.00,
        "deviation": -50000.00,
        "deviationPercent": -62.50
      },
      {
        "productId": "PRD-011",
        "productName": "Product K",
        "actualRevenue": 40000.00,
        "forecastRevenue": 70000.00,
        "deviation": -30000.00,
        "deviationPercent": -42.86
      },
      {
        "productId": "PRD-012",
        "productName": "Product L",
        "actualRevenue": 50000.00,
        "forecastRevenue": 75000.00,
        "deviation": -25000.00,
        "deviationPercent": -33.33
      }
    ]
  }
}
```

### Error Responses

#### 400 Bad Request - Missing Account ID

```json
{
  "success": false,
  "message": "Invalid query parameters",
  "errors": [
    {
      "field": "account_id",
      "message": "account_id parameter is required"
    }
  ]
}
```

#### 400 Bad Request - Invalid Date Format

```json
{
  "success": false,
  "message": "Invalid date format",
  "errors": [
    {
      "field": "from",
      "message": "Date must be in YYYY-MM format"
    }
  ]
}
```

#### 400 Bad Request - Invalid Date Range

```json
{
  "success": false,
  "message": "Invalid date range",
  "errors": [
    {
      "field": "to",
      "message": "End date must be greater than or equal to start date"
    }
  ]
}
```

## Implementation Architecture

### Layer Structure

```
Controller Layer (views.py)
    ↓
Service Layer (services.py)
    ↓
Repository Layer (repositories.py)
```

### Components

1. **Repository Layer**
   - Query actual revenue from invoices and invoice line items
   - Query forecast revenue from forecast table
   - Perform FULL OUTER JOIN between aggregations
   - Handle NULL values using COALESCE
   - Return raw aggregated data

2. **Service Layer**
   - Convert YYYY-MM to first/last day of month
   - Call repository methods
   - Calculate deviation and deviation percentage
   - Sort and rank products
   - Select top 3 and bottom 3 performers

3. **Controller Layer**
   - Validate query parameters
   - Call service layer
   - Map to response DTOs
   - Return standardized response format

## Database Indexes

### Required Indexes

Before creating indexes, verify if they already exist:

```sql
-- Check existing indexes
SELECT indexname FROM pg_indexes 
WHERE tablename IN ('invoices', 'forecast', 'invoice_line_items');
```

### Recommended Indexes

```sql
-- Invoices table
CREATE INDEX IF NOT EXISTS idx_invoices_invoice_date 
ON invoices(inv_invoice_date);

CREATE INDEX IF NOT EXISTS idx_invoices_status 
ON invoices(inv_status);

CREATE INDEX IF NOT EXISTS idx_invoices_valid 
ON invoices(inv_valid);

CREATE INDEX IF NOT EXISTS idx_invoices_account 
ON invoices(inv_account_id);

-- Forecast table
CREATE INDEX IF NOT EXISTS idx_forecast_arf_forecast_date 
ON forecast(arf_forecast_date);

CREATE INDEX IF NOT EXISTS idx_forecast_arf_product 
ON forecast(arf_product);

CREATE INDEX IF NOT EXISTS idx_forecast_arf_status 
ON forecast(arf_status);

CREATE INDEX IF NOT EXISTS idx_forecast_arf_account 
ON forecast(arf_account_id);

-- Invoice line items
CREATE INDEX IF NOT EXISTS idx_invoice_line_items_product_sku 
ON invoice_line_items(product_sku);

CREATE INDEX IF NOT EXISTS idx_invoice_line_items_valid 
ON invoice_line_items(ili_valid);
```

## Performance Considerations

1. **Database-Level Aggregation**
   - All SUM operations performed in database
   - No application-level aggregation

2. **FULL OUTER JOIN**
   - Ensures products with only forecast or only actual data are included
   - Use COALESCE to handle NULL values

3. **Division by Zero Protection**
   - Check forecastRevenue = 0 before calculating percentage
   - Return 0 for deviationPercent when forecastRevenue is 0

4. **Query Optimization**
   - Use appropriate indexes
   - Filter early in query execution
   - Limit results to top/bottom 3

## Implementation Checklist

- [ ] Create repository methods for actual and forecast revenue queries
- [ ] Implement service layer with deviation calculation logic
- [ ] Create controller endpoint with parameter validation
- [ ] Define request/response DTOs
- [ ] Add database indexes (if missing)
- [ ] Handle edge cases (no data, zero forecast, etc.)
- [ ] Follow existing project naming conventions
- [ ] Use dependency injection pattern
- [ ] Test with various date ranges

## Notes

- Uses existing project response wrapper structure
- No changes to existing modules required
- No frontend implementation needed
- Date conversion from YYYY-MM to full date range handled in service layer
- Safe handling of NULL and zero values throughout calculation pipeline
