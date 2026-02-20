# Feature: Product Performance Variance API (Forecast vs Actual)

## 🎯 Objective

Implement a **GET API** to fetch:

- Top 3 Performing Products
- Bottom 3 Performing Products

based on:

Deviation between:

Approved Forecast Value (RFC)
vs
Actual Invoice Revenue

for a given **month range** selected from UI.

Example:

2025-07 → 2025-12  
2026-02 → 2026-02  
etc.

---

## 📊 Business Logic

### Actual Revenue

Derived from:

invoice_line_items.net_price

Join:

invoice_line_items → invoices → products

Apply filters:

- invoices.invoice_date BETWEEN :from_date AND :to_date
- invoices.status = 'Closed'
- invoices.valid = true
- invoice_line_items.valid = true
- invoices.invoice_type != 'Credit Note'

Group by:

product

---

### Forecast Revenue

Derived from:

forecast.arf_approved_value

Apply filters:

- forecast.arf_forecast_date BETWEEN :from_date AND :to_date
- forecast.arf_status = 'Approved'

Group by:

forecast.arf_product

---

### Final Calculation

For each product:

actualRevenue = SUM(invoice_line_items.net_price)

forecastRevenue = SUM(forecast.arf_approved_value)

deviation = actualRevenue - forecastRevenue

deviationPercent =
    IF forecastRevenue = 0
    THEN 0
    ELSE (deviation / forecastRevenue) * 100

---

## 📥 Input

Query Params:

```
GET /api/products/performance?from=YYYY-MM&to=YYYY-MM
```

Convert internally to:

from_date = first day of from month  
to_date   = last day of to month  

---

## 📤 Response Format

Must follow existing default response wrapper already used in project.

Data payload must be:

```json
{
  "topPerformers": [
    {
      "productId": "",
      "productName": "",
      "actualRevenue": 0,
      "forecastRevenue": 0,
      "deviation": 0,
      "deviationPercent": 0
    }
  ],
  "bottomPerformers": [
    {
      "productId": "",
      "productName": "",
      "actualRevenue": 0,
      "forecastRevenue": 0,
      "deviation": 0,
      "deviationPercent": 0
    }
  ]
}
```

---

## ⚙️ Implementation Rules

- Follow existing project architecture
- Use existing:
    - Repository Layer
    - Service Layer
    - Controller Layer
    - Request / Response DTOs
- DO NOT introduce new response structure
- DO NOT affect any existing modules
- Use dependency injection where applicable
- Follow existing naming conventions

---

## 📌 Ranking Logic

Top Performers:

Highest deviation (DESC)
LIMIT 3

Bottom Performers:

Lowest deviation (ASC)
LIMIT 3

---

## 🚀 Performance Considerations

Before creating indexes:

Check if these indexes already exist:

- invoices(invoice_date)
- invoices(status)
- forecast(arf_forecast_date)
- forecast(arf_product)
- invoice_line_items(product_sku)

If index exists → DO NOTHING

If missing → Create index using migration approach used in project

Example:

PostgreSQL:

CREATE INDEX IF NOT EXISTS idx_invoice_date
ON invoices(invoice_date);

Follow project migration strategy.

---

## 🧠 Additional Notes

- Use FULL OUTER JOIN between Forecast and Actual Aggregations
- Handle NULL safely using COALESCE
- Do aggregation in DB layer only
- Do NOT calculate in application layer
- Handle forecastRevenue = 0 safely to avoid division by zero

---

## ✅ Deliverables

- Repository Query
- Service Logic
- Controller Endpoint
- DTO Mapping
- Optional Migration (only if index missing)

No frontend changes required.