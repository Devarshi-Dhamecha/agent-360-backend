# Users API - Frontend Integration Guide

Base URL: `/api/users/`  
Auth: `AllowAny` (no authentication required).

---

## Get All Users

**GET** `/api/users/`

Returns a paginated list of all active users with their basic information.

### Query Parameters

| Parameter   | Type   | Required | Default | Description                          |
|------------|--------|----------|---------|--------------------------------------|
| `page`     | int    | No       | 1       | Page number for pagination           |
| `page_size`| int    | No       | 20      | Number of items per page (max: 100)  |

### Response Fields

Each user object contains:

| Field       | Type   | Description                                    |
|------------|--------|------------------------------------------------|
| `id`       | string | User's Salesforce ID (unique identifier)       |
| `full_name`| string | User's complete name                           |
| `email`    | string | User's email address                           |
| `role`     | string | User's role name (null if no role assigned)    |

### Example Requests

```bash
# Get all users (first page)
curl -s -X GET "http://localhost:8000/api/users/"

# Get users with custom page size
curl -s -X GET "http://localhost:8000/api/users/?page_size=50"

# Get second page
curl -s -X GET "http://localhost:8000/api/users/?page=2"
```

---

## Response Examples

### Success Response (200 OK)

```json
{
  "success": true,
  "message": "Data retrieved successfully",
  "data": [
    {
      "id": "005xx000001234ABC",
      "full_name": "John Doe",
      "email": "john.doe@example.com",
      "role": "Sales Manager"
    },
    {
      "id": "005xx000001234DEF",
      "full_name": "Jane Smith",
      "email": "jane.smith@example.com",
      "role": "Account Executive"
    },
    {
      "id": "005xx000001234GHI",
      "full_name": "Bob Johnson",
      "email": "bob.johnson@example.com",
      "role": null
    }
  ],
  "meta": {
    "pagination": {
      "current_page": 1,
      "page_size": 20,
      "total_count": 3,
      "total_pages": 1,
      "has_next": false,
      "has_previous": false
    }
  }
}
```

### Empty Result (200 OK)

When no users are found:

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

### Validation Error (400 Bad Request)

When invalid query parameters are provided (e.g., invalid page_size):

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

### Server Error (500 Internal Server Error)

When an unexpected error occurs:

```json
{
  "success": false,
  "message": "An unexpected error occurred. Please try again later.",
  "error_code": "INTERNAL_ERROR"
}
```

---

## Error Responses

The API follows the project's standardized error response format:

### 400 - Bad Request

Invalid query parameters (e.g., page_size exceeds maximum):

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

## Frontend Integration

### Response Structure

All responses follow this structure:

**Success Response:**
```typescript
{
  success: true,
  message: string,
  data: User[],
  meta: {
    pagination: {
      current_page: number,
      page_size: number,
      total_count: number,
      total_pages: number,
      has_next: boolean,
      has_previous: boolean
    }
  }
}
```

**Error Response:**
```typescript
{
  success: false,
  message: string,
  error_code: string,
  errors?: Array<{
    field: string,
    message: string
  }>
}
```

---

## Notes

- Only active users (`usr_active = 1`) are returned
- Users are sorted alphabetically by full name
- The `role` field will be `null` if the user has no role assigned
- Maximum page size is 100 items
- Default page size is 20 items
- All responses follow the project's standardized format with `success`, `message`, `data`, and optional `meta` or `errors` fields
- Error responses include `error_code` for programmatic error handling
