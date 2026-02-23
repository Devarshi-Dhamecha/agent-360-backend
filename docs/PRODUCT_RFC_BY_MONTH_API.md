# Product RFC by Month API (Draft / Approved with Last Year)

## Overview

API endpoint to fetch **Request For Change (RFC)** data by product and month range: **current year** **both** draft and approved quantity and value (RFC Qty, RFC Value) in the same response—frontend switches by data key—and **last year** quantity and value (LY Qty, LY Value) for the same period. Supports **multiple product IDs** and a **month range (from / to)**. Used to power the “Update RFC” UI (e.g. category Herbicides: select products, month range, view Draft/Approved, see LY and current year data). If month range is not provided, behaviour is defined by default rules below.

## Confirmed API route (before implementation)

| Item | Value |
|------|--------|
| **Method** | `GET` |
| **Full URL** | `/api/products/rfc-by-month/` |
| **Django path** (in `apps/products/urls.py`) | `rfc-by-month/` |
| **URL name** (optional) | `rfc_by_month` |
| **Base** | `config/urls.py` mounts products at `api/products/`, so full path is `api/products/` + `rfc-by-month/` |

**Example:** `GET /api/products/rfc-by-month/?account_id=001XXX&product_ids=PRD-001,PRD-002&from=2026-02&to=2026-09`

## Query Parameters

| Parameter     | Type   | Required | Format              | Description |
|--------------|--------|----------|---------------------|-------------|
| `account_id` | string | Yes      | Salesforce ID       | Account to scope all data (invoices, forecasts). |
| `product_ids` | string | Yes      | Comma-separated IDs | One or more product Salesforce IDs (e.g. Roundup, Typhoon, Atranex). |
| `from`       | string | No*      | YYYY-MM             | Start month of range (e.g. 2026-02). See section "When from / to are provided vs not provided". “When from / to not received”. |
| `to`         | string | No*      | YYYY-MM             | End month of range (e.g. 2026-07). *See “When from / to not received”. |
### When from / to are provided vs not provided

**Response includes both Draft and Approved:** The API always returns **both** Draft and Approved RFC data in the same response. The frontend switches/toggles using **data keys** (e.g. `draftRfcQty`/`draftRfcValue` vs `approvedRfcQty`/`approvedRfcValue` per month). No `view` query parameter is used.

**Case 1 – User enters `from` and `to`:**  
Use that month range for the **current (RFC)** period. **Last year (LY)** = **same months, previous year** (same window shifted back one year).

| User enters   | Current (RFC) period | LY period        |
|---------------|----------------------|------------------|
| Feb 2026 – Sep 2026 | Feb 2026 – Sep 2026 | **Feb 2025 – Sep 2025** |
| Feb 2026 – Jul 2026 | Feb 2026 – Jul 2026 | Feb 2025 – Jul 2025 |

Example: `from=2026-02&to=2026-09` → Current = Feb 2026 through Sep 2026; **LY = Feb 2025 through Sep 2025**.

---

**Case 2 – User does not enter `from` and/or `to`:**  
**Calculate** the range from the **current month (today’s year and month)**:
- **Current (RFC) period:** from = **current month**, to = **same month next year**.  
  Example: if today is Feb 2026 → **Feb 2026 – Feb 2027** (13 months).
- **LY period:** Same window shifted back one year → **Feb 2025 – Feb 2026**.

Implementation: when from/to are omitted, set `from` = first day of **current month**, `to` = last day of **same month next year**; then LY = (from − 1 year) to (to − 1 year). When from/to are provided, use them as-is for current; LY = (from − 1 year) to (to − 1 year).

### Examples

```
# User enters range: Feb 2026 – Sep 2026 → Current Feb–Sep 2026, LY Feb–Sep 2025
GET /api/products/rfc-by-month/?account_id=001XXX&product_ids=PRD-001,PRD-002&from=2026-02&to=2026-09

# User enters range: Feb–Jul 2026 → LY Feb–Jul 2025
GET /api/products/rfc-by-month/?account_id=0011234567890ABC&product_ids=PRD-001,PRD-002,PRD-003&from=2026-02&to=2026-07

# User does not enter from/to → default: current month through same month next year; LY = that window back one year
GET /api/products/rfc-by-month/?account_id=001XXX&product_ids=PRD-001,PRD-002
```

---

## Business Logic

### Data Sources

- **Account:** `accounts.acc_sf_id` = `account_id` (scope for invoices and forecasts).
- **Products:** `products.prd_sf_id` IN `product_ids`.
- **Current year (RFC):** `arf_rolling_forecasts` – draft: `arf_draft_quantity`, `arf_draft_value`; approved: `arf_approved_quantity`, `arf_approved_value`. Key: `arf_account_id`, `arf_product_id`, `arf_forecast_date` (month).
- **Last year (LY):** `invoice_line_items` + `invoices` – `ili_quantity` (LY Qty), `ili_net_price` (LY Value). Same account and product; invoice date in **same calendar month range, previous year**.

### Last Year (LY) – Quantity and Value

**Purpose:** “Last year Qty” (LY Qty) and “Last year Value” (LY Value) for the **same** window as the current (RFC) range, **shifted back one year** (e.g. current Feb 2026–Feb 2027 → LY Feb 2025–Feb 2026).

**Source:**

- **LY Qty:** `invoice_line_items.ili_quantity`
- **LY Value:** `invoice_line_items.ili_net_price`

**Joins:**

- `invoice_line_items` → `invoices` (for account and date)

**Filters:**

- `invoices.inv_account_id` = :account_id
- `invoice_line_items.ili_product_id` IN :product_ids
- `invoices.inv_invoice_date` BETWEEN :ly_from_date AND :ly_to_date  
  - Where `ly_from_date` = from_date − 1 year, `ly_to_date` = to_date − 1 year (same window length, shifted back).  
  - Example: from=2026-02, to=2027-02 → LY 2025-02-01 to 2026-02-28; or from=2026-02, to=2026-07 → LY 2025-02-01 to 2025-07-31.
- `invoices.inv_status` IN ('Closed', 'Posted') — both count for LY so last year data appears when invoices exist in either status
- `invoices.inv_valid` = true
- `invoices.inv_invoice_type` != 'Credit Note'
- `invoice_line_items.ili_valid` = true
- (Optional) exclude credit notes if stored differently; align with other product performance APIs.

**Aggregation (per product, per month):**

- For each product and each month in the range:
  - **LY Qty:** `SUM(ili.ili_quantity)` for that product and that month (last year).
  - **LY Value:** `SUM(ili.ili_net_price)` for that product and that month (last year).

If a product has no invoices in a given month last year, return 0 for that month’s LY Qty and LY Value.

**Formula (date derivation):**

```
1. Resolve effective (from_date, to_date):
   - If user entered from and to: from_date = first day of from_month, to_date = last day of to_month.
     Example: from=2026-02, to=2026-09 → 2026-02-01 to 2026-09-30.
   - If user did NOT enter from and/or to: from_date = first day of current month (today),
     to_date = last day of same month next year.
     Example: today = Feb 2026 → 2026-02-01 to 2027-02-28.

2. Current (RFC) range: [from_date, to_date].

3. Last year (LY) range: same window shifted back one year (always):
   ly_from_date = from_date - 1 year
   ly_to_date   = to_date   - 1 year

   Examples:
   - User entered Feb 2026–Sep 2026 → LY = Feb 2025–Sep 2025.
   - Default (current month = Feb 2026) → current Feb 2026–Feb 2027, LY = Feb 2025–Feb 2026.
```

---

### Current Year – Draft RFC and Approved RFC (both returned)

**Purpose:** Return **both** Draft and Approved RFC data for each product and each month so the **frontend can switch using data keys** (e.g. show Draft or Approved view without a second request).

**Source:**

- **Draft:** `arf_rolling_forecasts.arf_draft_quantity`, `arf_rolling_forecasts.arf_draft_value` (rows where status is Draft, Pending_Approval, Fixes_Needed, or as per business rules).
- **Approved:** `arf_rolling_forecasts.arf_approved_quantity`, `arf_rolling_forecasts.arf_approved_value` (rows where `arf_status` = 'Approved').

**Filters:**

- `arf_rolling_forecasts.arf_account_id` = :account_id
- `arf_rolling_forecasts.arf_product_id` IN :product_ids
- `arf_rolling_forecasts.arf_forecast_date` BETWEEN :from_date AND :to_date (current year range)
- **Draft aggregation:** Include forecast rows in Draft (and optionally Pending_Approval / Fixes_Needed) status; sum draft qty/value.
- **Approved aggregation:** Include rows with `arf_status` = 'Approved'; sum approved qty/value.
- (Optional) `arf_rolling_forecasts.arf_active` = 1 if the schema has such a flag.

**Aggregation (per product, per month):**

- For each product and each month in the range, return **both**:
  - **Draft:** `draftRfcQty` = SUM(arf_draft_quantity), `draftRfcValue` = SUM(arf_draft_value)
  - **Approved:** `approvedRfcQty` = SUM(arf_approved_quantity), `approvedRfcValue` = SUM(arf_approved_value)

If there is no forecast row for a product in a given month, return 0 (or null; document which) for that month’s draft and approved qty/value.

**Formula:**

```
draftRfcQty     = SUM(arf_draft_quantity)   per product/month (Draft-status rows)
draftRfcValue   = SUM(arf_draft_value)      per product/month
approvedRfcQty  = SUM(arf_approved_quantity) per product/month (Approved-status rows)
approvedRfcValue= SUM(arf_approved_value)   per product/month
```

---

### Month Range and “Same Period Last Year”

- **Month range:** From and To are inclusive (first day of start month to last day of end month).
- **Last year range:** Same start and end **months**, previous **year**. No shift of months; only year is decremented by 1.
- **Per-month breakdown:** Response includes each month with LY Qty, LY Value, **and both** Draft (draftRfcQty, draftRfcValue) and Approved (approvedRfcQty, approvedRfcValue) so the frontend can toggle by key.

---

### Edge Cases

- **No invoices last year for a product/month:** LY Qty = 0, LY Value = 0.
- **No forecast for a product/month (current year):** Draft/Approved Qty and Value = 0 (or null; document which).
- **Empty product_ids:** Return 400/422 or empty data structure; document.
- **Invalid from/to (e.g. to before from):** Return 422 with a clear message.
- **Invalid product_ids (non-existent):** Either exclude and return data for valid IDs only, or return 404/422; document.
- **Account has no data:** Return structure with zeros (or empty rows) for all requested products and months.

---

## Response Format

### Success Response (200 OK)

Response includes **accountId**, **from**, **to**, **currencySymbol**, and **products** (each with **productId**, **productName**, **months**). Each month object includes **both** Draft and Approved data so the frontend can switch by key:

- **lyQty**, **lyValue** – last year (same window, previous year)
- **draftRfcQty**, **draftRfcValue** – current year draft RFC
- **approvedRfcQty**, **approvedRfcValue** – current year approved RFC

Example (frontend uses `draftRfcQty`/`draftRfcValue` or `approvedRfcQty`/`approvedRfcValue` to show Draft vs Approved view):

```json
{
  "success": true,
  "message": "RFC by month retrieved successfully",
  "data": {
    "accountId": "0011234567890ABC",
    "from": "2026-02",
    "to": "2026-07",
    "currencySymbol": "£",
    "products": [
      {
        "productId": "PRD-001",
        "productName": "Roundup",
        "months": [
          {
            "month": "2026-02",
            "monthLabel": "February 2026",
            "lyQty": 0,
            "lyValue": 35000.00,
            "draftRfcQty": 250,
            "draftRfcValue": 225000.00,
            "approvedRfcQty": 240,
            "approvedRfcValue": 216000.00
          },
          {
            "month": "2026-03",
            "monthLabel": "March 2026",
            "lyQty": 0,
            "lyValue": 35000.00,
            "draftRfcQty": 280,
            "draftRfcValue": 252000.00,
            "approvedRfcQty": 270,
            "approvedRfcValue": 243000.00
          }
        ]
      }
    ]
  }
}
```

### Error Responses

#### 422 – Missing account_id

```json
{
  "success": false,
  "message": "Invalid query parameters",
  "errors": [
    { "field": "account_id", "message": "account_id is required" }
  ]
}
```

#### 422 – Missing product_ids

```json
{
  "success": false,
  "message": "Invalid query parameters",
  "errors": [
    { "field": "product_ids", "message": "At least one product_id is required" }
  ]
}
```

#### 422 – Invalid month range (if from/to required or validated)

```json
{
  "success": false,
  "message": "Invalid date range",
  "errors": [
    { "field": "to", "message": "End month must be on or after start month" }
  ]
}
```

#### 422 – Invalid from or to format

```json
{
  "success": false,
  "message": "Invalid date format",
  "errors": [
    { "field": "from", "message": "Must be YYYY-MM" }
  ]
}
```

---

## Implementation Architecture

### Layer Structure

```
Controller (views.py)
    ↓
Service (e.g. rfc_by_month_services.py or in existing analytics_services)
    ↓
Models / Raw SQL: Invoice, InvoiceLineItem, ArfRollingForecast, Product
```

### Components

1. **Controller**
   - Parse query params: `account_id`, `product_ids` (split comma-separated or accept repeated param), `from`, `to`.
   - **Resolve range:** If from and to provided, use them (current = that range; LY = same range − 1 year). If not, default = current month through same month next year; LY = that window − 1 year.
   - Validate month range (from ≤ to, YYYY-MM format).
   - Call service; return standardized response (success, message, data) with **both** draft and approved data.

2. **Service**
   - Compute **last year** date range (same months, year - 1).
   - **LY:** Query invoice_line_items + invoices for account, product_ids, LY date range; aggregate by product and month (SUM ili_quantity, SUM ili_net_price).
   - **Current year:** Query arf_rolling_forecasts for account, product_ids, current year date range; aggregate **both** draft (arf_draft_quantity, arf_draft_value) and approved (arf_approved_quantity, arf_approved_value) by product and month, so each month has draftRfcQty, draftRfcValue, approvedRfcQty, approvedRfcValue.
   - Build list of months in range; for each product and month, attach LY, draft RFC, and approved RFC values (use 0 when no data).
   - Resolve currency symbol from account (e.g. acc_currency_iso_code) and attach to response.

3. **Data access**
   - Prefer single (or few) aggregated queries per “year” (LY vs current) to avoid N+1. Group by product_id and month (e.g. DATE_TRUNC('month', date)) for both invoices and forecasts.

---

## Database Indexes

Relevant for performance:

- **invoices:** `inv_account_id`, `inv_invoice_date`, `inv_status`, `inv_valid`
- **invoice_line_items:** `ili_invoice_id`, `ili_product_id`, `ili_valid`
- **arf_rolling_forecasts:** `arf_account_id`, `arf_product_id`, `arf_forecast_date`, `arf_status`
- **products:** `prd_sf_id`

---

## Performance Considerations

1. **Multiple product IDs:** Use `IN (:product_ids)` and keep product list size reasonable; consider a limit (e.g. max 50) and document it.
2. **Month range:** Limit range (e.g. max 12 or 24 months) to avoid very large payloads; document.
3. **Aggregation:** Do SUM and GROUP BY product, month in the database; avoid loading raw rows and aggregating in Python.
4. **Two time windows:** One set of queries for last year (invoices), one for current year (forecasts); can be two queries or CTEs in one SQL.

---

## Implementation Checklist

- [ ] Define endpoint path and method (GET).
- [ ] Implement **both cases**: (1) When user enters from and to, use that range; LY = same months previous year (e.g. Feb–Sep 2026 → LY Feb–Sep 2025). (2) When from/to not received, default = current month through same month next year; LY = that window back one year.
- [ ] Parse and validate **account_id**, **product_ids** (multiple), **from**, **to**, **view**.
- [ ] Implement **last year** logic: same month range, previous year; source invoice_line_items (ili_quantity, ili_net_price); filters (Closed, valid, no Credit Note); aggregate by product and month.
- [ ] Implement **current year** logic: arf_rolling_forecasts; return **both** Draft and Approved (draftRfcQty, draftRfcValue, approvedRfcQty, approvedRfcValue) per product and month.
- [ ] Build response: list of products, each with list of months and lyQty, lyValue, draftRfcQty, rfcValue (and/or approved fields).
- [ ] Use 0 (or null) for missing LY or RFC data per product/month.
- [ ] Add currency symbol from account.
- [ ] Add error responses (422) for validation.
- [ ] Add indexes if missing; consider limits on product count and month range.

---

## Notes

- **Only future months can be edited:** This applies to the **Update RFC** (save) flow, not necessarily to this GET. When implementing PUT/PATCH for “Save RFC”, enforce “only future months can be edited” in the service/validation layer.
- **Both Draft and Approved in one response:** The API returns both draft and approved RFC data; the frontend toggles using data keys (`draftRfcQty`/`draftRfcValue` vs `approvedRfcQty`/`approvedRfcValue`) without a second request.
- **Alignment with Update RFC UI:** The response supports the Update RFC screen: multiple products, month range, LY Qty, LY Value, and both Draft and Approved RFC Qty/Value per month.
- This document should be treated as the single source of truth for the “RFC by month” (with last year) API before implementation.

---

## Finding account_id and product_id that return non-zero data

To get **lyQty/lyValue** or **draftRfcQty/approvedRfcQty** non-zero, use an account and product that have invoices (Closed) or forecasts in the relevant date range. Run this in your DB to get one pair (adjust the date range if needed; below uses a 13‑month window from current month):

```sql
-- One account_id + product_id pair that has either LY invoice data or RFC forecast data
SELECT acc_sf_id AS account_id, prd_sf_id AS product_id
FROM accounts a
CROSS JOIN LATERAL (
  SELECT ili.ili_product_id AS prd_sf_id
  FROM invoice_line_items ili
  INNER JOIN invoices inv ON inv.inv_sf_id = ili.ili_invoice_id
  WHERE inv.inv_account_id = a.acc_sf_id
    AND inv.inv_status = 'Closed' AND inv.inv_valid = TRUE
    AND inv.inv_invoice_date BETWEEN (date_trunc('month', current_date) - interval '1 year')::date
      AND (date_trunc('month', current_date) + interval '1 year' - interval '1 day')::date
  LIMIT 1
) ly
LIMIT 1
;
-- If no LY data, try an account that has forecasts:
SELECT arf.arf_account_id AS account_id, arf.arf_product_id AS product_id
FROM arf_rolling_forecasts arf
WHERE arf.arf_active = 1
  AND arf.arf_forecast_date >= date_trunc('month', current_date)::date
  AND arf.arf_forecast_date <= (date_trunc('month', current_date) + interval '1 year')::date
LIMIT 1
;
```

Use the returned `account_id` and `product_id` in the API:  
`GET /api/products/rfc-by-month/?account_id=<account_id>&product_ids=<product_id>`
