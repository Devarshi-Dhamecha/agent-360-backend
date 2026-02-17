# Analytics API Module

## Overview

The Analytics API provides hierarchical data aggregation for sales analytics across three levels:
- **Family Level**: Aggregated by product family
- **Product Level**: Aggregated by individual products within a family
- **Invoice Level**: Aggregated by invoices for a specific product

## Architecture

The module follows a clean architecture pattern with clear separation of concerns:

```
analytics/
├── views.py         # API endpoint handlers (no business logic)
├── services.py      # Business logic and data processing
├── selectors.py     # Database queries (read-only)
├── serializers.py   # Request/response validation
├── urls.py          # URL routing
└── tests.py         # Unit tests
```

### Design Principles

- **Read-Only**: No data modifications, only aggregation queries
- **Service Layer**: All business logic in `AnalyticsService`
- **Selector Pattern**: All database queries in selector functions
- **Django ORM**: No raw SQL, optimized aggregation queries
- **SOLID Principles**: Single responsibility, dependency injection

## API Endpoint

### GET /api/analytics/

Retrieve hierarchical analytics data with actual sales, RFC (forecast), and last year sales.

#### Query Parameters

| Parameter | Required | Type | Description | Example |
|-----------|----------|------|-------------|---------|
| level | Yes | string | Aggregation level: `family`, `product`, or `invoice` | `family` |
| parent_id | Conditional | string | Parent ID for drill-down (required for `product` and `invoice` levels) | `Herbicides` |
| start_month | Yes | string | Start month in YYYY-MM format | `2025-03` |
| end_month | Yes | string | End month in YYYY-MM format | `2025-10` |
| top_n | No | integer | Limit results to top N records | `5` |
| ordering | No | string | Field to order by (prefix with `-` for descending) | `-actual_sales` |

#### Response Format

```json
{
  "success": true,
  "message": "Analytics fetched successfully",
  "data": {
    "level": "family",
    "start_month": "2025-03",
    "end_month": "2025-10",
    "total_actual_sales": 208000,
    "total_rfc": 201000,
    "total_last_year_sales": 185000,
    "chart_data": [
      {"label": "Herbicides", "value": 68000},
      {"label": "Fungicides", "value": 140000}
    ],
    "results": [
      {
        "id": "Herbicides",
        "name": "Herbicides",
        "status": null,
        "actual_sales": 68000,
        "rfc": 65000,
        "last_year_sales": 59000,
        "deviation_percent": 4.6,
        "is_drillable": true
      }
    ]
  }
}
```

## Usage Examples

### 1. Family Level Analytics

Get aggregated sales by product family:

```bash
GET /api/analytics/?level=family&start_month=2025-03&end_month=2025-10
```

### 2. Product Level Analytics

Get aggregated sales by products within a family:

```bash
GET /api/analytics/?level=product&parent_id=Herbicides&start_month=2025-03&end_month=2025-10
```

### 3. Invoice Level Analytics

Get aggregated sales by invoices for a specific product:

```bash
GET /api/analytics/?level=invoice&parent_id=PROD001&start_month=2025-03&end_month=2025-10
```

### 4. Top N Results

Get top 5 families by actual sales:

```bash
GET /api/analytics/?level=family&start_month=2025-03&end_month=2025-10&top_n=5&ordering=-actual_sales
```

## Business Rules

### Data Filtering

- Only includes `InvoiceLineItems` where `is_valid = True`
- Only includes `Invoices` where `status = 'Closed'`
- Date range is inclusive (first day of start_month to last day of end_month)

### Revenue Sources

- **Actual Sales**: Sum of `InvoiceLineItems.net_price`
- **RFC (Forecast)**: Sum of `Forecasts.revenue`
- **Last Year Sales**: Same as actual sales, shifted back 1 year

### Deviation Calculation

```python
if rfc > 0:
    deviation_percent = ((actual_sales - rfc) / rfc) * 100
else:
    deviation_percent = 0
```

Rounded to 2 decimal places.

## Performance Considerations

- Uses Django ORM aggregation functions (`Sum`, `Coalesce`, `F`)
- Leverages database indexes on:
  - `Products.family`
  - `Invoices.status`
  - `Invoices.invoice_date`
  - `InvoiceLineItems.is_valid`
  - `Forecasts.forecast_date`
- Avoids N+1 queries through proper use of `values()` and `annotate()`
- Minimal data transfer (only required fields)

## Testing

Run tests with:

```bash
python manage.py test apps.products.analytics
```

Test coverage includes:
- Parameter validation
- Date range conversion
- Deviation calculation
- Data merging logic
- Ordering and limiting
- API endpoint validation

## Error Handling

The API returns standardized error responses:

```json
{
  "success": false,
  "message": "Invalid query parameters",
  "errors": [
    {
      "field": "level",
      "message": "This field is required."
    }
  ]
}
```

Common error scenarios:
- Missing required parameters
- Invalid level value
- Missing parent_id for product/invoice levels
- Invalid month format
- Database query errors

## Future Enhancements

Potential improvements:
- Caching for frequently accessed aggregations
- Additional aggregation levels (e.g., by region, sales rep)
- Export functionality (CSV, Excel)
- Real-time updates via WebSocket
- Advanced filtering options
