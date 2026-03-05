# Update RFC API – Specification (Implementation Complete)

## Overview

API endpoint to **update** Request For Change (RFC) **draft** quantity in the `arf_rolling_forecasts` table. Used by the "Update RFC" UI when the user saves changes to **draft quantity** for one or more product–month combinations. The backend **accepts only `draftRfcQty`** from the user and stores it in `arf_draft_quantity`. Draft value is **calculated on retrieval** (not on update) as quantity × unit price. All updates are scoped by `account_id` and apply only to **future months** (business rule).

This document reflects the **actual implementation** of the Update RFC API.

---

## Confirmed API Route

| Item | Value |
|------|--------|
| **Method** | `PATCH` (partial update of draft RFC per product/month) |
| **Full URL** | `/api/products/update-rfc/` |
| **Django path** (in `apps/products/urls.py`) | `update-rfc/` |
| **URL name** | `update_rfc` |
| **Base** | `config/urls.py` mounts products at `api/products/`, so full path is `api/products/update-rfc/` |

**Example:** `PATCH /api/products/update-rfc/` with JSON body (see Request Body).

---

## Data Target: `arf_rolling_forecasts`

Updates are written to the **arf_rolling_forecasts** table. Relevant columns:

| Column | Purpose |
|--------|--------|
| `arf_id` | Primary key; used for direct RFC lookup (optional in request for faster lookup). |
| `arf_account_id` | Scope: which account (required for matching rows). |
| `arf_product_id` | Product Salesforce ID (required for matching when `rfcId` not provided). |
| `arf_forecast_date` | Month of the forecast (date: first day of month). Used to match which row(s) to update. |
| `arf_draft_quantity` | **Updated** by this API (from user input `draftRfcQty`). |
| `arf_draft_unit_price` | **Not sent by user.** Kept unchanged from existing row when present; used to compute value on retrieval. If missing, draft value is null. |
| `arf_draft_value` | **Calculated on retrieval** (not on update). Value = quantity × unit price (see Backend calculation below). |
| `arf_status` | Only rows in `Draft`, `Pending_Approval`, `Fixes_Needed`, or `Approved` are eligible for update (see Business Rules). |
| `arf_agent_modified_by` | Set to current user (Agent360) when updating. |
| `arf_agent_modified_date` | Set to current timestamp when updating. |
| `arf_updated_at` | Auto-updated by Django (auto_now). |
| `arf_active` | Only update rows where `arf_active = 1`. |

All other columns (e.g. approved fields, sync fields) are **not** modified by this API.

---

## Business Rules (Implemented)

1. **Only future months can be edited**  
   - For each requested `month` (YYYY-MM), the first day of that month must be **strictly after** "today" (server date).  
   - If any requested month is in the past or current month, the API rejects that item with reason "Only future months can be edited".

2. **Scope by account**  
   - Every update is scoped by `account_id`. Only rows with `arf_account_id` = `account_id` are considered.

3. **Eligible rows**  
   - Only forecast rows with `arf_status` IN (`Draft`, `Pending_Approval`, `Fixes_Needed`, `Approved`) may be updated.  
   - Rows with `arf_status` = `Frozen` are not editable and return error for those product/month pairs.

4. **Product and account validity**  
   - `account_id` must exist in `accounts` (e.g. `acc_sf_id`). Returns 404 if not found.
   - Each `product_id` in the payload must exist in `products` (e.g. `prd_sf_id`). Returns validation error if any product not found.

5. **Draft value is calculated on retrieval**  
   - The user sends **only** `draftRfcQty`. The backend stores this in `arf_draft_quantity`. Draft value is **calculated on retrieval** (not on update) as `arf_draft_value` = `arf_draft_quantity` × unit price. Unit price is taken from the existing row's `arf_draft_unit_price` (or fallback; see Backend calculation). The client does **not** send `draftRfcValue` or `draftRfcUnitPrice`.

6. **No create/upsert behavior**  
   - If no row exists for (account_id, product_id, forecast_date), the API returns an error for that product/month with reason "No editable forecast row found for this product and month".

7. **Partial success supported**  
   - If some items fail validation or row lookup, the API returns 200 with `updated` and `notUpdated` lists. Items that fail do not block other items from being updated.

---

## Request Body

**Content-Type:** `application/json`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `accountId` | string | Yes | Salesforce Account ID; scope for all updates. |
| `updates` | array | Yes | List of per–product/month updates (see below). |

**Element of `updates`:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `rfcId` | integer | No | RFC ID for direct lookup (faster than product+month search). If provided, `productId` and `month` are optional but recommended for error messages. |
| `productId` | string | Conditional | Product Salesforce ID (e.g. PRD-001). Required if `rfcId` not provided. |
| `month` | string | Conditional | Month in `YYYY-MM` format (e.g. 2026-03). Must be a **future month** (see Business Rules). Required if `rfcId` not provided. |
| `draftRfcQty` | number | Yes | Draft quantity for that product/month. Must be non-negative decimal with max 16 digits and 2 decimal places. |

The user does **not** send `draftRfcValue` or `draftRfcUnitPrice`; the backend calculates draft value on retrieval (see **Backend calculation** below).

**Example request body (using productId + month):**

```json
{
  "accountId": "0011234567890ABC",
  "updates": [
    {
      "productId": "PRD-001",
      "month": "2026-03",
      "draftRfcQty": 280
    },
    {
      "productId": "PRD-001",
      "month": "2026-04",
      "draftRfcQty": 300
    },
    {
      "productId": "PRD-002",
      "month": "2026-03",
      "draftRfcQty": 150
    }
  ]
}
```

**Example request body (using rfcId for faster lookup):**

```json
{
  "accountId": "0011234567890ABC",
  "updates": [
    {
      "rfcId": 12345,
      "draftRfcQty": 280
    },
    {
      "rfcId": 12346,
      "draftRfcQty": 300
    }
  ]
}
```

---

## Backend Calculation (Draft Value and Unit Price)

- **Input from user:** `draftRfcQty` only.
- **Stored:** `arf_draft_quantity` = `draftRfcQty` (as Decimal with precision NUMERIC(16,2)).
- **Unit price source (in order of preference):**
  1. Existing forecast row's `arf_draft_unit_price` (if present).
  2. Else existing row's `arf_approved_unit_price` (if present).
  3. Else `arf_draft_unit_price` remains null and `arf_draft_value` = null.
- **Draft value (calculated on retrieval):**  
  `arf_draft_value` = `arf_draft_quantity` × unit price (when unit price is available); otherwise `arf_draft_value` = null.
- **Precision:** NUMERIC(16,2); rounded to 2 decimal places.

**Note:** Draft value is **not** stored on update; it is calculated dynamically when retrieved via the RFC by Month API.

---

## Validation Rules (Implemented)

| # | Rule | Response |
|---|------|----------|
| 1 | `accountId` is required and non-empty. | 422 Validation Error |
| 2 | `updates` is required, must be a non-empty array. | 422 Validation Error |
| 3 | Each `month` is in format YYYY-MM and represents a **future month** (first day of month > today). | 422 Validation Error (per item) |
| 4 | Each `productId` exists in `products`. | 422 Validation Error (lists missing products) |
| 5 | `accountId` exists in `accounts`. | 404 Not Found |
| 6 | `draftRfcQty` is required per item and must be a valid non-negative number. | 200 with item in `notUpdated` |
| 7 | `draftRfcQty` is within allowed precision (NUMERIC(16,2)) and non-negative. | 200 with item in `notUpdated` |
| 8 | No duplicate (productId, month) within a single request. | 422 Validation Error |
| 9 | Target row exists and is in editable status (Draft/Pending_Approval/Fixes_Needed/Approved). | 200 with item in `notUpdated` |
| 10 | Max size of `updates` array (configurable via `ValidationConstants.MAX_RFC_UPDATES`, default 100). | 422 Validation Error |

---

## Response Format

### Success Response (200 OK)

Returns standard envelope with `success`, `message`, `data`.

**Example:**

```json
{
  "success": true,
  "message": "RFC updated successfully",
  "data": {
    "accountId": "0011234567890ABC",
    "updatedCount": 3,
    "updated": [
      {
        "rfcId": 12345,
        "productId": "PRD-001",
        "month": "2026-03"
      },
      {
        "rfcId": 12346,
        "productId": "PRD-001",
        "month": "2026-04"
      },
      {
        "rfcId": 12347,
        "productId": "PRD-002",
        "month": "2026-03"
      }
    ],
    "notUpdated": []
  }
}
```

**Partial success example (some items fail):**

```json
{
  "success": true,
  "message": "RFC updated successfully",
  "data": {
    "accountId": "0011234567890ABC",
    "updatedCount": 2,
    "updated": [
      {
        "rfcId": 12345,
        "productId": "PRD-001",
        "month": "2026-03"
      },
      {
        "rfcId": 12346,
        "productId": "PRD-001",
        "month": "2026-04"
      }
    ],
    "notUpdated": [
      {
        "rfcId": null,
        "productId": "PRD-002",
        "month": "2026-02",
        "reason": "Only future months can be edited"
      }
    ]
  }
}
```

### Error Responses

#### 400 – Bad Request (Invalid JSON)

```json
{
  "success": false,
  "message": "Invalid request body",
  "errors": [
    {
      "field": "body",
      "message": "JSON body is required"
    }
  ]
}
```

#### 422 – Validation Error (Missing or Invalid Fields)

```json
{
  "success": false,
  "message": "Validation failed",
  "errors": [
    {
      "field": "accountId",
      "message": "accountId is required"
    }
  ]
}
```

#### 422 – Validation Error (Past Month)

```json
{
  "success": false,
  "message": "Validation failed",
  "errors": [
    {
      "field": "updates[0].month",
      "message": "Only future months can be edited"
    }
  ]
}
```

#### 422 – Validation Error (Duplicate Product/Month)

```json
{
  "success": false,
  "message": "Validation failed",
  "errors": [
    {
      "field": "updates",
      "message": "Duplicate product/month in request"
    }
  ]
}
```

#### 422 – Validation Error (Product Not Found)

```json
{
  "success": false,
  "message": "Validation failed",
  "errors": [
    {
      "field": "productId",
      "message": "Products not found: PRD-999"
    }
  ]
}
```

#### 404 – Account Not Found

```json
{
  "success": false,
  "message": "Account not found",
  "errors": [
    {
      "field": "accountId",
      "message": "Account not found"
    }
  ],
  "resourceType": "Account"
}
```

---

## Implementation Architecture

### Layer Structure

```
Controller (UpdateRfcAPIView in views.py)
    ↓
Service (update_rfc() in rfc_services.py)
    ↓
Model: ArfRollingForecast (arf_rolling_forecasts)
```

### Implementation Details

1. **Controller (UpdateRfcAPIView)**  
   - Parses JSON body: `accountId`, `updates`.  
   - Validates structure: required fields, non-empty arrays, max size.
   - Validates account exists in `accounts` table.
   - Validates all products exist in `products` table.
   - Detects duplicate (productId, month) pairs.
   - Resolves current user from `request.user` (if authenticated).
   - Calls `rfc_services.update_rfc()` with validated payload.
   - Returns standard API response envelope.

2. **Service (update_rfc in rfc_services.py)**  
   - For each update item:
     - If `rfcId` provided: lookup row directly by `arf_id`, `arf_account_id`, status, and active flag.
     - Else: parse month to date, check if future month, lookup row by account_id, product_id, forecast_date, status, and active flag.
     - If row found and editable: set `arf_draft_quantity` = request `draftRfcQty`; set `arf_agent_modified_by` and `arf_agent_modified_date`; save.
     - If row not found or not editable: add to `notUpdated` list with reason.
   - Returns dict with `accountId`, `updatedCount`, `updated[]`, `notUpdated[]`.

3. **Model (ArfRollingForecast)**  
   - Primary key: `arf_id` (AutoField).
   - Status choices: Draft, Pending_Approval, Approved, Fixes_Needed, Frozen.
   - Draft fields: `arf_draft_quantity`, `arf_draft_unit_price`, `arf_draft_value`.
   - Audit fields: `arf_agent_modified_by` (FK to User), `arf_agent_modified_date`.
   - Active flag: `arf_active` (SmallIntegerField, default=1).

### Editable Statuses

Defined in `rfc_services.py`:
```python
ARF_EDITABLE_STATUSES = ("Draft", "Pending_Approval", "Fixes_Needed", "Approved")
```

---

## Authentication & Authorization

- **Authentication:** Endpoint uses `permission_classes = [AllowAny]` (no auth required currently).
- **User identity:** Current user resolved from `request.user` if authenticated; used to set `arf_agent_modified_by`.
- **Authorization:** No role/account-level checks currently enforced (can be added as needed).
- **Audit:** `arf_agent_modified_by` and `arf_agent_modified_date` are set on every successful update.

---

## Alignment with RFC by Month API

- The **GET** `/api/products/rfc-by-month/` API returns draft and approved RFC data; see `docs/PRODUCT_RFC_BY_MONTH_API.md`.  
- This **PATCH** Update RFC API is the "save" counterpart: it updates the **draft quantity** in `arf_rolling_forecasts` that the GET API reads.  
- Draft value is **calculated on retrieval** by the GET API using: `SUM(arf_draft_quantity * arf_draft_unit_price)` per product/month.
- After a successful PATCH, a subsequent GET to `rfc-by-month` for the same account/products/months will reflect the new draft quantities and recalculated draft values.

---

## Implementation Checklist (Completed)

- [x] Route and method (PATCH) implemented and documented.
- [x] Request/response schema and validation rules implemented (user sends **draftRfcQty** only; backend stores quantity).
- [x] Business rules implemented (future month only, eligible statuses, no create/upsert).
- [x] Controller: parse body, validate, call service, return standard envelope.
- [x] Service: resolve rows by rfcId or product+month; set `arf_draft_quantity` from request; update audit fields; handle not-found/ineligible with partial success.
- [x] Error responses (400, 422, 404) implemented as per this doc.
- [x] Authentication and authorization applied (AllowAny with optional user tracking).
- [x] Serializers: `UpdateRfcRequestSerializer`, `UpdateRfcResponseSerializer`, `UpdateRfcItemSerializer`.
- [x] Docs/OpenAPI schema updated with request/response examples.

---

## Document Control

- **Purpose:** Specification and implementation reference for the Update RFC API.  
- **Status:** Implementation Complete.
- **Target table:** `arf_rolling_forecasts`.  
- **Related docs:** 
  - `PRODUCT_RFC_BY_MONTH_API.md` (GET RFC by month).
  - `apps/products/views.py` (UpdateRfcAPIView).
  - `apps/products/rfc_services.py` (update_rfc function).
  - `apps/products/serializers.py` (UpdateRfc* serializers).
- **Last updated:** March 2026.
