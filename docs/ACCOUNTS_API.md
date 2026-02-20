# Accounts API

Base URL: `/api/accounts/`  
Auth: `AllowAny` (no authentication required).

---

## Endpoints

| Method | Endpoint                          | Description                              |
|--------|-----------------------------------|------------------------------------------|
| GET    | `/api/accounts/`                  | List all accounts                        |
| GET    | `/api/accounts/user/{user_id}/`   | List accounts by user (owner) ID         |

---

## 1) List All Accounts

**GET** `/api/accounts/`

Returns a list of all accounts. If pagination parameters (`page` or `page_size`) are provided, returns paginated results. Otherwise, returns all accounts without pagination.

### Query Parameters

| Parameter   | Type   | Required | Default | Description                                      |
|------------|--------|----------|---------|--------------------------------------------------|
| `page`     | int    | No       | -       | Page number (if provided, enables pagination)    |
| `page_size`| int    | No       | -       | Number of items per page (max: 100, if provided, enables pagination) |

### Response Fields

Each account object contains:

| Field              | Type    | Description                                    |
|-------------------|---------|------------------------------------------------|
| `id`              | string  | Account's Salesforce ID (unique identifier)    |
| `name`            | string  | Account name                                   |
| `owner_id`        | string  | Owner's Salesforce ID (null if not assigned)   |
| `account_number`  | string  | Account number                                 |
| `currency_iso_code`| string | Currency ISO code (e.g., EUR, USD)            |
| `credit_limit`    | decimal | Credit limit amount                            |
| `active`          | int     | Active status (1 = active, 0 = inactive)       |

### Example Requests

```bash
# Get all accounts (no pagination)
curl -s -X GET "http://localhost:8000/api/accounts/"

# Get accounts with pagination (first page, default size 20)
curl -s -X GET "http://localhost:8000/api/accounts/?page=1"

# Get accounts with custom page size
curl -s -X GET "http://localhost:8000/api/accounts/?page=1&page_size=50"

# Get second page
curl -s -X GET "http://localhost:8000/api/accounts/?page=2&page_size=20"
```

### Success Response - All Data (200 OK)

When no pagination parameters are provided:

```json
{
  "success": true,
  "message": "Data retrieved successfully",
  "data": [
    {
      "id": "001xx000001234ABC",
      "name": "Acme Corp",
      "owner_id": "005xx000001234ABC",
      "account_number": "ACC-001",
      "currency_iso_code": "EUR",
      "credit_limit": "100000.00",
      "active": 1
    },
    {
      "id": "001xx000001234DEF",
      "name": "Global Industries",
      "owner_id": "005xx000001234XYZ",
      "account_number": "ACC-002",
      "currency_iso_code": "USD",
      "credit_limit": "250000.00",
      "active": 1
    }
  ]
}
```

### Success Response - Paginated (200 OK)

When pagination parameters (`page` or `page_size`) are provided:

```json
{
  "success": true,
  "message": "Data retrieved successfully",
  "data": [
    {
      "id": "001xx000001234ABC",
      "name": "Acme Corp",
      "owner_id": "005xx000001234ABC",
      "account_number": "ACC-001",
      "currency_iso_code": "EUR",
      "credit_limit": "100000.00",
      "active": 1
    },
    {
      "id": "001xx000001234DEF",
      "name": "Global Industries",
      "owner_id": "005xx000001234XYZ",
      "account_number": "ACC-002",
      "currency_iso_code": "USD",
      "credit_limit": "250000.00",
      "active": 1
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

## 2) Get Accounts by User ID

**GET** `/api/accounts/user/{user_id}/`

Returns a list of accounts filtered by owner (user) Salesforce ID. If pagination parameters (`page` or `page_size`) are provided, returns paginated results. Otherwise, returns all accounts for that user without pagination.

### Path Parameters

| Parameter | Type   | Required | Description                          |
|-----------|--------|----------|--------------------------------------|
| `user_id` | string | Yes      | User's Salesforce ID (owner)         |

### Query Parameters

| Parameter   | Type   | Required | Default | Description                                      |
|------------|--------|----------|---------|--------------------------------------------------|
| `page`     | int    | No       | -       | Page number (if provided, enables pagination)    |
| `page_size`| int    | No       | -       | Number of items per page (max: 100, if provided, enables pagination) |

### Response Fields

Same as List All Accounts endpoint.

### Example Requests

```bash
# Get all accounts for a specific user (no pagination)
curl -s -X GET "http://localhost:8000/api/accounts/user/005xx000001234ABC/"

# Get accounts with pagination
curl -s -X GET "http://localhost:8000/api/accounts/user/005xx000001234ABC/?page=1"

# Get accounts with custom page size
curl -s -X GET "http://localhost:8000/api/accounts/user/005xx000001234ABC/?page=1&page_size=50"

# Get second page
curl -s -X GET "http://localhost:8000/api/accounts/user/005xx000001234ABC/?page=2&page_size=20"
```

### Success Response - All Data (200 OK)

When no pagination parameters are provided:

```json
{
  "success": true,
  "message": "Data retrieved successfully",
  "data": [
    {
      "id": "001xx000001234ABC",
      "name": "Acme Corp",
      "owner_id": "005xx000001234ABC",
      "account_number": "ACC-001",
      "currency_iso_code": "EUR",
      "credit_limit": "100000.00",
      "active": 1
    },
    {
      "id": "001xx000001234GHI",
      "name": "Tech Solutions Ltd",
      "owner_id": "005xx000001234ABC",
      "account_number": "ACC-003",
      "currency_iso_code": "EUR",
      "credit_limit": "150000.00",
      "active": 1
    }
  ]
}
```

### Success Response - Paginated (200 OK)

When pagination parameters (`page` or `page_size`) are provided:

```json
{
  "success": true,
  "message": "Data retrieved successfully",
  "data": [
    {
      "id": "001xx000001234ABC",
      "name": "Acme Corp",
      "owner_id": "005xx000001234ABC",
      "account_number": "ACC-001",
      "currency_iso_code": "EUR",
      "credit_limit": "100000.00",
      "active": 1
    },
    {
      "id": "001xx000001234GHI",
      "name": "Tech Solutions Ltd",
      "owner_id": "005xx000001234ABC",
      "account_number": "ACC-003",
      "currency_iso_code": "EUR",
      "credit_limit": "150000.00",
      "active": 1
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

### Empty Result (200 OK)

When user has no accounts (with or without pagination):

```json
{
  "success": true,
  "message": "Data retrieved successfully",
  "data": []
}
```

Or with pagination:

```json
{
  "success": true,
  "message": "Data retrieved successfully",
  "data": [],
  "meta": {
    "pagination": {
      "current_page": 1,
      "page_size": 20,
      "total_count": 0,
      "total_pages": 0,
      "has_next": false,
      "has_previous": false
    }
  }
}
```

### Missing User ID (400 Bad Request)

When user_id is empty or not provided:

```json
{
  "success": false,
  "message": "User ID is required",
  "error_code": "REQUIRED_FIELD_MISSING",
  "errors": [
    {
      "field": "user_id",
      "message": "User ID cannot be empty"
    }
  ]
}
```

---

## Error Responses

The API follows the project's standardized error response format:

### 400 - Bad Request

**Invalid query parameters** (e.g., page_size exceeds maximum):

```json
{
  "success": false,
  "message": "Validation failed",
  "error_code": "VALIDATION_ERROR",
  "errors": [
    {
      "field": "page_size",
      "message": "Ensure this value is less than or equal to 100."
    }
  ]
}
```

**Missing required field** (for user-specific endpoint):

```json
{
  "success": false,
  "message": "User ID is required",
  "error_code": "REQUIRED_FIELD_MISSING",
  "errors": [
    {
      "field": "user_id",
      "message": "User ID cannot be empty"
    }
  ]
}
```

### 500 - Internal Server Error

Unexpected server error:

```json
{
  "success": false,
  "message": "An unexpected error occurred. Please try again later.",
  "error_code": "INTERNAL_ERROR"
}
```

---

## Notes

- Accounts are sorted alphabetically by name
- The `owner_id` field will be `null` if no owner is assigned
- Pagination is optional:
  - If `page` or `page_size` parameters are provided, the response will be paginated
  - If no pagination parameters are provided, all data is returned without pagination
  - Default page size when paginating is 20 items
  - Maximum page size is 100 items
- All responses follow the project's standardized format with `success`, `message`, `data`, and optional `meta` or `errors` fields
- Error responses include `error_code` for programmatic error handling
- The `/api/accounts/user/{user_id}/` endpoint requires a valid user_id in the URL path
- Swagger UI will show `page` and `page_size` as optional input parameters
