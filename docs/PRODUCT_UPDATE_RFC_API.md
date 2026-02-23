# Update RFC API – Specification (Pre-Implementation Validation)

## Overview

API endpoint to **update** Request For Change (RFC) **draft** values in the `arf_rolling_forecasts` table. Used by the “Update RFC” UI when the user saves changes to **draft quantity** for one or more product–month combinations. The backend **accepts only `draftRfcQty`** from the user and **calculates `draftRfcValue`** (and keeps or derives unit price) on the server. All updates are scoped by `account_id` and apply only to **future months** (business rule).

This document is the **single source of truth for validation** before implementing the Update RFC API. It should be reviewed and approved before any code is written.

---

## Confirmed API Route (Proposed)

| Item | Value |
|------|--------|
| **Method** | `PATCH` (partial update of draft RFC per product/month) |
| **Full URL** | `/api/products/update-rfc/` |
| **Django path** (in `apps/products/urls.py`) | `update-rfc/` |
| **URL name** (optional) | `update_rfc` |
| **Base** | `config/urls.py` mounts products at `api/products/`, so full path is `api/products/` + `update-rfc/` |

**Example:** `PATCH /api/products/update-rfc/` with JSON body (see Request Body).

---

## Data Target: `arf_rolling_forecasts`

Updates are written to the **arf_rolling_forecasts** table. Relevant columns:

| Column | Purpose |
|--------|--------|
| `arf_account_id` | Scope: which account (required for matching rows). |
| `arf_product_id` | Product Salesforce ID (required for matching). |
| `arf_forecast_date` | Month of the forecast (date: first day of month). Used to match which row(s) to update. |
| `arf_draft_quantity` | **Updated** by this API (from user input `draftRfcQty`). |
| `arf_draft_unit_price` | **Not sent by user.** Kept unchanged from existing row when present; used to compute value. If missing, see Backend calculation. |
| `arf_draft_value` | **Calculated by backend.** Value = quantity × unit price (see Backend calculation below). |
| `arf_status` | Only rows in `Draft`, `Pending_Approval`, or `Fixes_Needed` are eligible for update (see Business Rules). |
| `arf_agent_modified_by` | Set to current user (Agent360) when updating. |
| `arf_agent_modified_date` | Set to current timestamp when updating. |
| `arf_last_modified_by_id` | Set to current user ID when updating. |
| `arf_updated_at` | Auto-updated (e.g. `auto_now`). |
| `arf_active` | Only update rows where `arf_active = 1` (if applicable). |

All other columns (e.g. approved fields, sync fields) are **not** modified by this API.

---

## Business Rules (Must Validate Before Implementation)

1. **Only future months can be edited**  
   - For each requested `month` (YYYY-MM), the first day of that month must be **strictly after** “today” (server date).  
   - If any requested month is in the past or current month, the API must reject that item (or the whole request)—document choice (see Validation below).

2. **Scope by account**  
   - Every update is scoped by `account_id`. Only rows with `arf_account_id` = `account_id` are considered.

3. **Eligible rows**  
   - Only forecast rows with `arf_status` IN (`Draft`, `Pending_Approval`, `Fixes_Needed`) may be updated.  
   - Rows with `arf_status` = `Approved` or `Frozen` must **not** be modified by this API (return 409 or 422 for those product/month pairs).

4. **Product and account validity**  
   - `account_id` must exist in `accounts` (e.g. `acc_sf_id`).  
   - Each `product_id` in the payload must exist in `products` (e.g. `prd_sf_id`).  
   - Optionally: enforce that the product is valid for the account (e.g. used in forecasts or invoices for that account)—document if required.

5. **Draft value is backend-calculated**  
   - The user sends **only** `draftRfcQty`. The backend computes `arf_draft_value` = `arf_draft_quantity` × unit price. Unit price is taken from the existing row’s `arf_draft_unit_price` (or fallback; see Backend calculation). The client does **not** send `draftRfcValue` or `draftRfcUnitPrice`.

6. **Create vs update**  
   - If no row exists for (account_id, product_id, forecast_date): **Option A** – return 404 for that product/month; **Option B** – create a new row (upsert) with draft values and appropriate status. Document the chosen behaviour.

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
| `productId` | string | Yes | Product Salesforce ID (e.g. PRD-001). |
| `month` | string | Yes | Month in `YYYY-MM` format (e.g. 2026-03). Must be a **future month** (see Business Rules). |
| `draftRfcQty` | number | Yes | Draft quantity for that product/month. **Only draft field sent by the user.** |

The user does **not** send `draftRfcValue` or `draftRfcUnitPrice`; the backend calculates draft value (see **Backend calculation** below).

**Example request body:**

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

---

## Backend calculation (draft value and unit price)

- **Input from user:** `draftRfcQty` only.
- **Stored:** `arf_draft_quantity` = `draftRfcQty`.
- **Unit price source (in order of preference):**
  1. Existing forecast row’s `arf_draft_unit_price` (if present).
  2. Else existing row’s `arf_approved_unit_price` (if present).
  3. Else leave `arf_draft_unit_price` null and set `arf_draft_value` = null, or use a defined fallback (e.g. last-year average from invoices)—to be confirmed.
- **Draft value:**  
  `arf_draft_value` = `arf_draft_quantity` × unit price (when unit price is available); otherwise `arf_draft_value` = null (or per fallback rule).
- **Precision:** Use NUMERIC(16,2); round to 2 decimal places.

**Optional (to confirm during validation):**

- `modifiedByUserId` or similar in body vs. from auth/session (e.g. JWT) for `arf_agent_modified_by` / `arf_last_modified_by_id`.

---

## Validation Rules (Pre-Implementation Checklist)

Before implementing, confirm and document:

| # | Rule | Rejection (e.g. 422) |
|---|------|----------------------|
| 1 | `accountId` is required and non-empty. | Missing `accountId` |
| 2 | `updates` is required, must be a non-empty array (if at least one update is required). | Missing or empty `updates` |
| 3 | Each `month` is in format YYYY-MM and represents a **future month** (first day of month > today). | Invalid or past/current month |
| 4 | Each `productId` exists in `products`. | Invalid or unknown product |
| 5 | `accountId` exists in `accounts`. | Invalid or unknown account |
| 6 | `draftRfcQty` is required per item and must be a valid non-negative number. | Missing or invalid draftRfcQty |
| 7 | `draftRfcQty` is within allowed precision (e.g. NUMERIC(16,2)) and non-negative. | Invalid number |
| 8 | No duplicate (productId, month) within a single request. | Duplicate product/month in request |
| 9 | Target row exists and is in status Draft / Pending_Approval / Fixes_Needed (if “no create”); or define upsert behaviour. | 404 or 409 for ineligible status |
| 10 | Max size of `updates` array (e.g. 100 items) to avoid abuse. | Too many items |

---

## Response Format

### Success Response (200 OK)

Return a consistent envelope: `success`, `message`, `data`. Optionally include how many rows were updated and/or the updated values.

**Example:**

```json
{
  "success": true,
  "message": "RFC updated successfully",
  "data": {
    "accountId": "0011234567890ABC",
    "updatedCount": 3,
    "updated": [
      { "productId": "PRD-001", "month": "2026-03" },
      { "productId": "PRD-001", "month": "2026-04" },
      { "productId": "PRD-002", "month": "2026-03" }
    ]
  }
}
```

Alternative: return full updated draft values per product/month in `data` for the frontend to refresh without a second GET.

### Error Responses

#### 400 – Bad Request (e.g. invalid JSON)

```json
{
  "success": false,
  "message": "Invalid request body",
  "errors": [
    { "field": "body", "message": "Invalid JSON" }
  ]
}
```

#### 422 – Validation Error (e.g. missing accountId)

```json
{
  "success": false,
  "message": "Validation failed",
  "errors": [
    { "field": "accountId", "message": "accountId is required" }
  ]
}
```

#### 422 – Past or current month

```json
{
  "success": false,
  "message": "Validation failed",
  "errors": [
    { "field": "updates[0].month", "message": "Only future months can be edited" }
  ]
}
```

#### 404 – Account or product not found (if applicable)

```json
{
  "success": false,
  "message": "Account not found",
  "errors": [
    { "field": "accountId", "message": "Account not found" }
  ]
}
```

#### 409 – Row not editable (e.g. status Approved/Frozen)

```json
{
  "success": false,
  "message": "One or more forecast rows cannot be updated",
  "data": {
    "notUpdated": [
      { "productId": "PRD-001", "month": "2026-03", "reason": "Forecast already approved" }
    ]
  }
}
```

(Use 409 only if partial updates are not supported; otherwise document “best effort” and return 200 with `updated` and `notUpdated` in `data`.)

---

## Implementation Architecture (Proposed)

### Layer Structure

```
Controller (views.py) – parse body, validate, call service
    ↓
Service (e.g. update_rfc_services.py or in rfc_services.py)
    ↓
Model: ArfRollingForecast (arf_rolling_forecasts)
```

### Steps (High Level)

1. **Controller**  
   - Parse JSON body: `accountId`, `updates`.  
   - Validate structure and run validation rules (future month, product exists, account exists, non-negative numbers, no duplicates, max size).  
   - Resolve current user for `arf_agent_modified_by` / `arf_last_modified_by_id` (from request/session/JWT).  
   - Call service with validated payload.

2. **Service**  
   - For each (account_id, product_id, month):  
     - Resolve `forecast_date` = first day of month.  
     - Find row: `arf_account_id`, `arf_product_id`, `arf_forecast_date`, `arf_status` IN (`Draft`, `Pending_Approval`, `Fixes_Needed`), `arf_active = 1`.  
     - If no row: apply “no create” (return error for that item) or “upsert” (create row)—per validation choice.  
     - If row exists and editable: set `arf_draft_quantity` = request `draftRfcQty`; resolve unit price from existing row (draft then approved, or fallback); set `arf_draft_value` = quantity × unit price (or null if no unit price); set `arf_agent_modified_by`, `arf_agent_modified_date`, `arf_last_modified_by_id`; save.  
   - Collect updated / notUpdated and return to controller.

3. **Response**  
   - Return 200 with `data.updatedCount` and `data.updated` (and optionally `data.notUpdated` with reasons).

---

## Security & Permissions (To Confirm)

- **Authentication:** Endpoint must require authenticated user (e.g. JWT/session).  
- **Authorization:** Confirm whether any role/account check is required (e.g. user can only update forecasts for accounts they have access to).  
- **Audit:** `arf_agent_modified_by` and `arf_agent_modified_date` must be set on every update.

---

## Alignment with Existing RFC by Month API

- The **GET** `/api/products/rfc-by-month/` API returns draft and approved RFC data; see `docs/PRODUCT_RFC_BY_MONTH_API.md`.  
- This **PATCH** Update RFC API is the “save” counterpart: it updates the **draft** values in `arf_rolling_forecasts` that the GET API reads.  
- After a successful PATCH, a subsequent GET to `rfc-by-month` for the same account/products/months will reflect the new draft values.

---

## Open Points for Validation

Before implementation, confirm:

1. **Future month rule:** Reject entire request if any month is past/current, or reject only those items and process the rest (partial success)?  
2. **Create vs update:** If no row exists for (account, product, month), return 404 for that item or create a new row (upsert)?  
3. **Unit price fallback:** When the existing row has no `arf_draft_unit_price` and no `arf_approved_unit_price`, set `arf_draft_value` = null, or use another source (e.g. last-year average unit price from invoices)?  
4. **Partial success:** If some items fail (e.g. status Approved), return 200 with `updated` and `notUpdated` or return 409 and do not update any?  
5. **Max items:** Maximum number of entries in `updates` per request (e.g. 50 or 100).  
6. **User identity:** How `arf_agent_modified_by` and `arf_last_modified_by_id` are populated (body vs auth/session).

---

## Implementation Checklist (After Validation)

- [ ] Route and method (PATCH) agreed and documented.
- [ ] Request/response schema and validation rules signed off (user sends **draftRfcQty** only; backend calculates value).
- [ ] Business rules (future month only, eligible statuses, create vs update) confirmed.
- [ ] Controller: parse body, validate, call service, return standard envelope.
- [ ] Service: resolve rows; set `arf_draft_quantity` from request; compute `arf_draft_value` = qty × unit price (unit price from existing row or fallback); update audit fields; handle not-found/ineligible.
- [ ] Error responses (400, 422, 404, 409) implemented as per this doc.
- [ ] Authentication and authorization applied.
- [ ] Unit/integration tests for success and validation paths.
- [ ] Docs/Postman example updated with final request/response samples.

---

## Document Control

- **Purpose:** Pre-implementation validation for the Update RFC API.  
- **Target table:** `arf_rolling_forecasts`.  
- **Related doc:** `PRODUCT_RFC_BY_MONTH_API.md` (GET RFC by month).  
- This document should be treated as the single source of truth for the Update RFC API **until implementation begins**; any change after validation should be reflected here before coding.
