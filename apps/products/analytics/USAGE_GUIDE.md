# Analytics API - Quick Usage Guide

## Quick Start

The Analytics API provides a hierarchical drill-down view of sales data across three levels:

```
Family → Products → Invoices
```

## Basic Usage

### 1. Start at Family Level

View all product families:

```http
GET /api/analytics/?level=family&start_month=2025-03&end_month=2025-10
```

Response includes:
- List of all product families
- Actual sales, RFC, and last year sales for each
- `is_drillable: true` indicates you can drill down

### 2. Drill Down to Products

Click on a family (e.g., "Herbicides") to see its products:

```http
GET /api/analytics/?level=product&parent_id=Herbicides&start_month=2025-03&end_month=2025-10
```

Response includes:
- All products in the "Herbicides" family
- Sales metrics for each product
- `is_drillable: true` indicates you can drill down further

### 3. Drill Down to Invoices

Click on a product (e.g., "PROD001") to see its invoices:

```http
GET /api/analytics/?level=invoice&parent_id=PROD001&start_month=2025-03&end_month=2025-10
```

Response includes:
- All invoices containing this product
- Invoice number and status
- `is_drillable: false` (end of hierarchy)

## Advanced Features

### Sorting

Sort by any metric (default is `-actual_sales`):

```http
# Top performers by actual sales (descending)
GET /api/analytics/?level=family&start_month=2025-03&end_month=2025-10&ordering=-actual_sales

# Lowest RFC (ascending)
GET /api/analytics/?level=family&start_month=2025-03&end_month=2025-10&ordering=rfc

# Highest deviation
GET /api/analytics/?level=family&start_month=2025-03&end_month=2025-10&ordering=-deviation_percent
```

Available sort fields:
- `actual_sales` / `-actual_sales`
- `rfc` / `-rfc`
- `last_year_sales` / `-last_year_sales`
- `deviation_percent` / `-deviation_percent`

### Top N Results

Limit results to top performers:

```http
# Top 5 families by sales
GET /api/analytics/?level=family&start_month=2025-03&end_month=2025-10&top_n=5

# Top 10 products in a family
GET /api/analytics/?level=product&parent_id=Herbicides&start_month=2025-03&end_month=2025-10&top_n=10
```

### Date Ranges

Specify any month range:

```http
# Single month
GET /api/analytics/?level=family&start_month=2025-03&end_month=2025-03

# Quarter
GET /api/analytics/?level=family&start_month=2025-01&end_month=2025-03

# Year
GET /api/analytics/?level=family&start_month=2025-01&end_month=2025-12

# Custom range
GET /api/analytics/?level=family&start_month=2024-11&end_month=2025-02
```

## Understanding the Response

### Response Structure

```json
{
  "success": true,
  "message": "Analytics fetched successfully",
  "data": {
    "level": "family",
    "start_month": "2025-03",
    "end_month": "2025-10",
    "total_actual_sales": 208000,      // Sum of all results
    "total_rfc": 201000,                // Sum of all forecasts
    "total_last_year_sales": 185000,   // Sum of last year
    "chart_data": [                     // Ready for charting
      {"label": "Herbicides", "value": 68000}
    ],
    "results": [                        // Detailed records
      {
        "id": "Herbicides",
        "name": "Herbicides",
        "status": null,                 // Only for invoices
        "actual_sales": 68000,
        "rfc": 65000,
        "last_year_sales": 59000,
        "deviation_percent": 4.6,       // (actual - rfc) / rfc * 100
        "is_drillable": true            // Can drill down?
      }
    ]
  }
}
```

### Key Metrics Explained

- **actual_sales**: Real revenue from closed invoices
- **rfc**: Revenue forecast (what was expected)
- **last_year_sales**: Same period last year (for comparison)
- **deviation_percent**: How much actual differs from forecast
  - Positive = exceeded forecast
  - Negative = below forecast
  - 0 = no forecast available

### Chart Data

The `chart_data` array is pre-formatted for visualization:
- Use `label` for chart labels
- Use `value` for chart values
- Already sorted and limited by your parameters

## Common Use Cases

### Dashboard Overview

Get top 5 families for a dashboard widget:

```http
GET /api/analytics/?level=family&start_month=2025-01&end_month=2025-12&top_n=5&ordering=-actual_sales
```

### Performance Analysis

Compare actual vs forecast for a specific family:

```http
GET /api/analytics/?level=product&parent_id=Herbicides&start_month=2025-01&end_month=2025-12&ordering=-deviation_percent
```

### Year-over-Year Comparison

The API automatically includes last year's data for the same period:

```http
GET /api/analytics/?level=family&start_month=2025-03&end_month=2025-10
```

This will compare:
- Current: March 2025 - October 2025
- Last Year: March 2024 - October 2024

### Product Deep Dive

Analyze all invoices for a specific product:

```http
GET /api/analytics/?level=invoice&parent_id=PROD001&start_month=2025-01&end_month=2025-12
```

## Error Handling

### Common Errors

**Missing required parameter:**
```json
{
  "success": false,
  "message": "Invalid query parameters",
  "errors": [
    {"field": "level", "message": "This field is required."}
  ]
}
```

**Missing parent_id for drill-down:**
```json
{
  "success": false,
  "message": "parent_id is required for level 'product'"
}
```

**Invalid month format:**
```json
{
  "success": false,
  "message": "Invalid query parameters",
  "errors": [
    {"field": "start_month", "message": "Enter a valid value."}
  ]
}
```

## Integration Examples

### JavaScript/Fetch

```javascript
async function getAnalytics(level, startMonth, endMonth, parentId = null) {
  const params = new URLSearchParams({
    level,
    start_month: startMonth,
    end_month: endMonth,
  });
  
  if (parentId) {
    params.append('parent_id', parentId);
  }
  
  const response = await fetch(`/api/analytics/?${params}`);
  const data = await response.json();
  
  if (data.success) {
    return data.data;
  } else {
    throw new Error(data.message);
  }
}

// Usage
const familyData = await getAnalytics('family', '2025-03', '2025-10');
const productData = await getAnalytics('product', '2025-03', '2025-10', 'Herbicides');
```

### Python/Requests

```python
import requests

def get_analytics(level, start_month, end_month, parent_id=None, top_n=None):
    params = {
        'level': level,
        'start_month': start_month,
        'end_month': end_month,
    }
    
    if parent_id:
        params['parent_id'] = parent_id
    
    if top_n:
        params['top_n'] = top_n
    
    response = requests.get('http://localhost:8000/api/analytics/', params=params)
    data = response.json()
    
    if data['success']:
        return data['data']
    else:
        raise Exception(data['message'])

# Usage
family_data = get_analytics('family', '2025-03', '2025-10')
product_data = get_analytics('product', '2025-03', '2025-10', parent_id='Herbicides', top_n=5)
```

## Tips & Best Practices

1. **Start Broad**: Always start at family level for overview
2. **Use top_n**: Limit results for better performance and UX
3. **Cache Results**: Consider caching frequently accessed date ranges
4. **Handle Nulls**: Some families/products may have null values
5. **Check is_drillable**: Use this flag to enable/disable drill-down UI
6. **Use chart_data**: Pre-formatted for easy visualization
7. **Monitor Deviation**: High deviation_percent indicates forecast accuracy issues
