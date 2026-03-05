# Product RFC by Month API (Draft / Approved with Last Year) – Implementation Complete

## Overview

API endpoint to fetch **Request For Change (RFC)** data by product and month range: **current year** **both** draft and approved quantity, value, and unit price (RFC Qty, RFC Value, RFC Unit Price) in the same response—frontend switches by data key—and **last year** quantity and value (LY Qty, LY Value) for the same period. Supports **multiple product IDs** and a **month range (from / to)**. Used to power the "Update RFC" UI (e.g. category Herbicides: select products, month range, view Draft/Approved, see LY and current year data). If month range is not provided, default range is current month through same month next year.

## Confirmed API Route

| Item | Value |
|------|--------|
| **Method** | `GET` |
| **Full URL** | `/api/products/rfc-by-month/` |
| **Django path** (in `apps/products/urls.py`) | `rfc-by-month/` |
| **URL name** | `rfc_by_month` |
| **Base** | `config/urls.py` mounts products at `api/products/`, so full path is `api/products/rfc-by-month/` |

**Example:** `GET /api/products/rfc-by-month/?account_id=001XXX&product_ids=PRD-001,PRD-002&from=2026-02&to=2026-09`

## Query Parameters

| Parameter     | Type   | Required | Format              | Description |
|--------------|--------|----------|---------------------|-------------|
| `account_id` | string | Yes      | Salesforce ID       | Account to scope all data (invoices, forecasts). |
| `product_ids` | string | Yes      | Comma-separated IDs | One or more product Salesforce IDs (e.g. PRD-001, PRD-002). |
| `from`       | string | No       | YYYY-MM             | Start month of range (e.g. 2026-02). Optional; default = current month. |
| `to`         | string | No       | YYYY-MM             | End month of range (e.g. 2026-07). Optional; default = same month next year. |

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
**Calculate** the range from the **current month (today's year and month)**:
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

## Business Logic (Implemented)

### Data Sources

- **Account:** `accounts.acc_sf_id` = `account_id` (scope for invoices and forecasts).
- **Products:** `products.prd_sf_id` IN `product_ids`.
- **Current year (RFC):** `arf_rolling_forecasts` – draft: `arf_draft_quantity`, `arf_draft_unit_price`, `arf_draft_value`; approved: `arf_approved_quantity`, `arf_approved_unit_price`, `arf_approved_value`; **rejection reason:** `arf_rejection_reason` (one per product/month when present). Key: `arf_account_id`, `arf_product_id`, `arf_forecast_date` (month).
- **Last year (LY):** `invoice_line_items` + `invoices` – `ili_quantity` (LY Qty), `ili_net_price` (LY Value). Same account and product; invoice date in **same calendar month range, previous year**.

### Last Year (LY) – Quantity and Value

**Purpose:** "Last year Qty" (LY Qty) and "Last year Value" (LY Value) for the **same** window as the current (RFC) range, **shifted back one year** (e.g. current Feb 2026–Feb 2027 → LY Feb 2025–Feb 2026).

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

**Aggregation (per product, per month):**

- For each product and each month in the range:
  - **LY Qty:** `SUM(ili.ili_quantity)` for that product and that month (last year).
  - **LY Value:** `SUM(ili.ili_net_price)` for that product and that month (last year).

If a product has no invoices in a given month last year, return 0 for that month's LY Qty and LY Value.

---

### Current Year – Draft RFC and Approved RFC (both returned)

**Purpose:** Return **both** Draft and Approved RFC data for each product and each month so the **frontend can switch using data keys** (e.g. show Draft or Approved view without a second request).

**Source:**

- **Draft:** `arf_rolling_forecasts.arf_draft_quantity`, `arf_rolling_forecasts.arf_draft_unit_price`, `arf_rolling_forecasts.arf_draft_value` (rows where status is Draft, Pending_Approval, Fixes_Needed, or Approved).
- **Approved:** `arf_rolling_forecasts.arf_approved_quantity`, `arf_rolling_forecasts.arf_approved_unit_price`, `arf_rolling_forecasts.arf_approved_value` (rows where `arf_status` = 'Approved').

**Filters:**

- `arf_rolling_forecasts.arf_account_id` = :account_id
- `arf_rolling_forecasts.arf_product_id` IN :product_ids
- `arf_rolling_forecasts.arf_forecast_date` BETWEEN :from_date AND :to_date (current year range)
- `arf_rolling_forecasts.arf_active` = 1

**Aggregation (per product, per month):**

- For each product and each month in the range, return **both**:
  - **Draft:** `draftRfcQty` = SUM(arf_draft_quantity), `draftRfcValue` = SUM(arf_draft_quantity * arf_draft_unit_price), `draftRfcUnitPrice` = MAX(arf_draft_unit_price) (one per product/month; null when none)
  - **Approved:** `approvedRfcQty` = SUM(arf_approved_quantity), `approvedRfcValue` = SUM(arf_approved_quantity * arf_approved_unit_price), `approvedRfcUnitPrice` = MAX(arf_approved_unit_price) (one per product/month; null when none)

If there is no forecast row for a product in a given month, return 0 for that month's draft and approved qty/value, and null for unit prices.

**Formula:**

```
draftRfcQty        = SUM(arf_draft_quantity)    per product/month
draftRfcValue      = SUM(arf_draft_quantity * arf_draft_unit_price) per product/month
draftRfcUnitPrice  = MAX(arf_draft_unit_price) per product/month (null when none)
approvedRfcQty     = SUM(arf_approved_quantity) per product/month
approvedRfcValue   = SUM(arf_approved_quantity * arf_approved_unit_price) per product/month
approvedRfcUnitPrice = MAX(arf_approved_unit_price) per product/month (null when none)
```

---

### Month Range and "Same Period Last Year"

- **Month range:** From and To are inclusive (first day of start month to last day of end month).
- **Last year range:** Same start and end **months**, previous **year**. No shift of months; only year is decremented by 1.
- **Per-month breakdown:** Response includes each month with LY Qty, LY Value, **and both** Draft (draftRfcQty, draftRfcValue, draftRfcUnitPrice) and Approved (approvedRfcQty, approvedRfcValue, approvedRfcUnitPrice) so the frontend can toggle by key.

---

### Edge Cases

- **No invoices last year for a product/month:** LY Qty = 0, LY Value = 0.
- **No forecast for a product/month (current year):** Draft/Approved Qty and Value = 0; Unit Price = null.
- **Empty product_ids:** Return 422 validation error.
- **Invalid from/to (e.g. to before from):** Return 422 with a clear message.
- **Invalid product_ids (non-existent):** Return 422 validation error.
- **Account has no data:** Return structure with zeros for all requested products and months.

---

## Response Format

### Success Response (200 OK)

Response includes **accountId**, **from**, **to**, **currencySymbol**, and **products** (each with **productId**, **productName**, **months**). Each month object includes **both** Draft and Approved data so the frontend can switch by key:

- **lyQty**, **lyValue** – last year (same window, previous year)
- **draftRfcQty**, **draftRfcValue**, **draftRfcUnitPrice** – current year draft RFC (unit price per product/month; null when none)
- **approvedRfcQty**, **approvedRfcValue**, **approvedRfcUnitPrice** – current year approved RFC (unit price per product/month; null when none)
- **rejectionReason** – optional; from `arf_rolling_forecasts.arf_rejection_reason` (one per product/month when present; null when none)
- **rfcId** – RFC ID for reference

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
            "rfcId": 12345,
            "month": "2026-02",
            "monthLabel": "February 2026",
            "lyQty": 0.0,
            "lyValue": 35000.00,
            "draftRfcQty": 250.0,
            "draftRfcValue": 225000.00,
            "draftRfcUnitPrice": 900.00,
            "approvedRfcQty": 240.0,
            "approvedRfcValue": 216000.00,
            "approvedRfcUnitPrice": 900.00,
            "rejectionReason": null
          },
          {
            "rfcId": 12346,
            "month": "2026-03",
            "monthLabel": "March 2026",
            "lyQty": 0.0,
            "lyValue": 35000.00,
            "draftRfcQty": 280.0,
            "draftRfcValue": 252000.00,
            "draftRfcUnitPrice": 900.00,
            "approvedRfcQty": 270.0,
            "approvedRfcValue": 243000.00,
            "approvedRfcUnitPrice": 900.00,
            "rejectionReason": "Insufficient supporting market data"
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

#### 422 – Invalid month range (to before from)

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
Controller (RfcByMonthAPIView in views.py)
    ↓
Service (get_rfc_by_month() in rfc_services.py)
    ↓
Models: Invoice, InvoiceLineItem, ArfRollingForecast, Product
```

### Components

1. **Controller (RfcByMonthAPIView)**
   - Parse query params: `account_id`, `product_ids` (comma-separated), `from`, `to`.
   - **Resolve range:** If from and to provided, use them (current = that range; LY = same range − 1 year). If not, default = current month through same month next year; LY = that window − 1 year.
   - Validate month range (from ≤ to, YYYY-MM format).
   - Call service; return standardized response (success, message, data) with **both** draft and approved data.

2. **Service (get_rfc_by_month)**
   - Compute **last year** date range (same months, year - 1).
   - **LY:** Query invoice_line_items + invoices for account, product_ids, LY date range; aggregate by product and month (SUM ili_quantity, SUM ili_net_price).
   - **Current year:** Query arf_rolling_forecasts for account, product_ids, current year date range; aggregate **both** draft (SUM arf_draft_quantity, SUM(arf_draft_quantity * arf_draft_unit_price), MAX(arf_draft_unit_price)) and approved (SUM arf_approved_quantity, SUM(arf_approved_quantity * arf_approved_unit_price), MAX(arf_approved_unit_price)) by product and month, so each month has draftRfcQty, draftRfcValue, draftRfcUnitPrice, approvedRfcQty, approvedRfcValue, approvedRfcUnitPrice.
   - Build list of months in range; for each product and month, attach LY, draft RFC, and approved RFC values (use 0 when no data; null for unit price when none).
   - Resolve currency symbol from account (e.g. acc_currency_iso_code) and attach to response.

3. **Data Access**
   - Prefer aggregated queries per "year" (LY vs current) to avoid N+1. Group by product_id and month (e.g. DATE_TRUNC('month', date)) for both invoices and forecasts.

---

## Database Indexes

Relevant for performance:

- **invoices:** `inv_account_id`, `inv_invoice_date`, `inv_status`, `inv_valid`
- **invoice_line_items:** `ili_invoice_id`, `ili_product_id`, `ili_valid`
- **arf_rolling_forecasts:** `arf_account_id`, `arf_product_id`, `arf_forecast_date`, `arf_status`, `arf_active`
- **products:** `prd_sf_id`

---

## Performance Considerations

1. **Multiple product IDs:** Use `IN (:product_ids)` and keep product list size reasonable; consider a limit (e.g. max 50) and document it.
2. **Month range:** Limit range (e.g. max 24 months) to avoid very large payloads; document.
3. **Aggregation:** Do SUM and GROUP BY product, month in the database; avoid loading raw rows and aggregating in Python.
4. **Two time windows:** One set of queries for last year (invoices), one for current year (forecasts); can be two queries or CTEs in one SQL.

---

## Implementation Checklist (Completed)

- [x] Define endpoint path and method (GET).
- [x] Implement **both cases**: (1) When user enters from and to, use that range; LY = same months previous year. (2) When from/to not received, default = current month through same month next year; LY = that window back one year.
- [x] Parse and validate **account_id**, **product_ids** (multiple), **from**, **to**.
- [x] Implement **last year** logic: same month range, previous year; source invoice_line_items (ili_quantity, ili_net_price); filters (Closed/Posted, valid, no Credit Note); aggregate by product and month.
- [x] Implement **current year** logic: arf_rolling_forecasts; return **both** Draft and Approved (draftRfcQty, draftRfcValue, draftRfcUnitPrice, approvedRfcQty, approvedRfcValue, approvedRfcUnitPrice) per product and month.
- [x] Build response: list of products, each with list of months and lyQty, lyValue, draftRfcQty, draftRfcValue, draftRfcUnitPrice, approvedRfcQty, approvedRfcValue, approvedRfcUnitPrice, rfcId, rejectionReason.
- [x] Use 0 for missing LY or RFC data per product/month; null for unit prices when none.
- [x] Add currency symbol from account.
- [x] Add error responses (422) for validation.
- [x] Serializers: `RfcByMonthResponseSerializer`, `RfcByMonthProductSerializer`, `RfcByMonthItemSerializer`.
- [x] Docs/OpenAPI schema updated with request/response examples.

---

## Notes

- **Only future months can be edited:** This applies to the **Update RFC** (PATCH) flow, not to this GET. When using the Update RFC API, only future months can be edited.
- **Both Draft and Approved in one response:** The API returns both draft and approved RFC data; the frontend toggles using data keys (`draftRfcQty`/`draftRfcValue` vs `approvedRfcQty`/`approvedRfcValue`) without a second request.
- **Alignment with Update RFC API:** The response supports the Update RFC screen: multiple products, month range, LY Qty, LY Value, and both Draft and Approved RFC Qty/Value/Unit Price per month. After updating via PATCH, the next GET will reflect the new draft quantities and recalculated draft values.
- **Draft value calculation:** Draft value is calculated on retrieval as SUM(arf_draft_quantity * arf_draft_unit_price) per product/month, not stored on update.

---

## Document Control

- **Purpose:** Specification and implementation reference for the RFC by Month API.  
- **Status:** Implementation Complete.
- **Related docs:** 
  - `PRODUCT_UPDATE_RFC_API.md` (PATCH Update RFC).
  - `apps/products/views.py` (RfcByMonthAPIView).
  - `apps/products/rfc_services.py` (get_rfc_by_month function).
  - `apps/products/serializers.py` (RfcByMonth* serializers).
- **Last updated:** March 2026.
