# Complaints & Cases API

Base URL: `/api/complaints-cases/`  
Auth: `AllowAny` (no authentication required).

---

## Endpoint list

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/complaints-cases/summary/` | Summary counts (open, closed, total) |
| GET | `/api/complaints-cases/` | List cases with filters and pagination |
| GET | `/api/complaints-cases/{case_id}/` | Case detail with counts |
| GET | `/api/complaints-cases/{case_id}/comments/` | Comments for case (latest first) |
| GET | `/api/complaints-cases/{case_id}/timeline/` | Timeline (case history) for case (latest first) |

---

## 1) Summary

**GET** `/api/complaints-cases/summary/`

**Query params:**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `account_id` | string | Yes | Account Salesforce ID to scope summary counts |

**Response (200):**
```json
{
  "success": true,
  "message": "Summary retrieved successfully",
  "data": {
    "open_count": 42,
    "total_count": 100,
    "closed_count": 58
  }
}
```

**Sample curl:**
```bash
curl -s -X GET "http://localhost:8000/api/complaints-cases/summary/?account_id=001xx000001234ABC"
```

---

## 2) List cases

**GET** `/api/complaints-cases/`

Returns cases with filters and ordering. If pagination parameters (`page` or `page_size`) are provided, returns paginated results. Otherwise, returns all cases without pagination.

**Query params:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `status` | string | `all` | `open` \| `closed` \| `all` |
| `search` | string | - | Search in subject / case number |
| `account_id` | string | - | Filter by account SF id |
| `opened_from` | date | - | Opened date from (YYYY-MM-DD) |
| `opened_to` | date | - | Opened date to (YYYY-MM-DD) |
| `ordering` | string | `-opened_at` | `opened_at`, `-opened_at`, `last_modified`, `-last_modified` |
| `page` | int | - | Page number (if provided, enables pagination) |
| `page_size` | int | - | Page size (max 100, if provided, enables pagination) |

Invalid `status` or `ordering` returns **400** with validation errors.

**Response - All Data (200):**

When no pagination parameters are provided:

```json
{
  "success": true,
  "message": "Data retrieved successfully",
  "data": [
    {
      "id": "500xx000001234ABC",
      "case_number": "00001001",
      "title": "Login issue",
      "status": "Open",
      "opened_at": "2024-02-15",
      "opened_at_display": "15/02/2024",
      "comments_count": 3,
      "timeline_count": 5,
      "priority": "High",
      "account_id": "001xx000001234ABC",
      "owner_id": "005xx000001234ABC"
    }
  ]
}
```

**Response - Paginated (200):**

When pagination parameters (`page` or `page_size`) are provided:
```json
{
  "success": true,
  "message": "Data retrieved successfully",
  "data": [
    {
      "id": "500xx000001234ABC",
      "case_number": "00001001",
      "title": "Login issue",
      "status": "Open",
      "opened_at": "2024-02-15",
      "opened_at_display": "15/02/2024",
      "comments_count": 3,
      "timeline_count": 5,
      "priority": "High",
      "account_id": "001xx000001234ABC",
      "owner_id": "005xx000001234ABC"
    }
  ],
  "meta": {
    "pagination": {
      "current_page": 1,
      "page_size": 20,
      "total_count": 100,
      "total_pages": 5,
      "has_next": true,
      "has_previous": false
    }
  }
}
```

**Sample curl:**
```bash
# All open cases (no pagination)
curl -s -X GET "http://localhost:8000/api/complaints-cases/?status=open"

# All open cases with pagination
curl -s -X GET "http://localhost:8000/api/complaints-cases/?status=open&page=1&page_size=20"

# Search and date range (no pagination)
curl -s -X GET "http://localhost:8000/api/complaints-cases/?search=login&opened_from=2024-01-01&opened_to=2024-02-28"

# By account and ordering with pagination
curl -s -X GET "http://localhost:8000/api/complaints-cases/?account_id=001xx000001234ABC&ordering=-last_modified&page=1"
```

---

## 3) Case detail

**GET** `/api/complaints-cases/{case_id}/`

**Response (200):**
```json
{
  "success": true,
  "message": "Case retrieved successfully",
  "data": {
    "id": "500xx000001234ABC",
    "case_number": "00001001",
    "title": "Login issue",
    "description": "Customer cannot log in after password reset.",
    "status": "Open",
    "opened_at": "2024-02-15",
    "opened_at_display": "15/02/2024",
    "comments_count": 3,
    "timeline_count": 5,
    "priority": "High",
    "account_id": "001xx000001234ABC",
    "owner_id": "005xx000001234ABC"
  }
}
```

**404** if `case_id` not found.

**Sample curl:**
```bash
curl -s -X GET "http://localhost:8000/api/complaints-cases/500xx000001234ABC/"
```

---

## 4) Case comments

**GET** `/api/complaints-cases/{case_id}/comments/`

Returns comments **latest first**.

**Response (200):**
```json
{
  "success": true,
  "message": "Comments retrieved successfully",
  "data": [
    {
      "comment_id": 102,
      "body": "Updated the case with latest info.",
      "created_at": "2024-02-16T14:30:00.000000Z",
      "created_by_id": "005xx000001234ABC",
      "created_by_name": "John Doe",
      "is_published": true
    }
  ]
}
```

**404** if `case_id` not found.

**Sample curl:**
```bash
curl -s -X GET "http://localhost:8000/api/complaints-cases/500xx000001234ABC/comments/"
```

---

## 5) Case timeline

**GET** `/api/complaints-cases/{case_id}/timeline/`

Returns case history events **latest first**.

**Response (200):**
```json
{
  "success": true,
  "message": "Timeline retrieved successfully",
  "data": [
    {
      "event_id": "012xx000001234ABC",
      "field": "Status",
      "old_value": "New",
      "new_value": "Working",
      "created_at": "2024-02-16T10:00:00.000000Z",
      "created_by_id": "005xx000001234ABC",
      "created_by_name": "Jane Smith"
    }
  ]
}
```

**404** if `case_id` not found.

**Sample curl:**
```bash
curl -s -X GET "http://localhost:8000/api/complaints-cases/500xx000001234ABC/timeline/"
```

---

## Error responses

- **400** – Invalid query params (e.g. `status`, `ordering`, date format). Body includes `errors` or field-specific messages.
- **422** – Missing required `account_id` in summary endpoint.
- **404** – Case not found (detail, comments, timeline).
- **500** – Server error (handled by project exception handler).

All error responses follow the project format, e.g.:
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": [{"field": "status", "message": "Invalid status. Allowed: open, closed, all"}]
}
```

---

## Notes

- Cases are sorted by the specified ordering parameter (default: `-opened_at`)
- Pagination is optional:
  - If `page` or `page_size` parameters are provided, the response will be paginated
  - If no pagination parameters are provided, all data is returned without pagination
  - Default page size when paginating is 20 items
  - Maximum page size is 100 items
- All responses follow the project's standardized format with `success`, `message`, `data`, and optional `meta` or `errors` fields
- Error responses include `error_code` for programmatic error handling
- Swagger UI will show `page` and `page_size` as optional input parameters
