# Campaigns & Tasks API

Base URL: `/api/campaigns/`  
Auth: `AllowAny` (no authentication required).

---

## Endpoints

| Method | Endpoint                | Description                                      |
|--------|-------------------------|--------------------------------------------------|
| GET    | `/api/campaigns/`       | List campaigns with mapped tasks by account      |
| GET    | `/api/campaigns/tasks/` | List tasks by campaign ID                        |

---

## 1) List Campaigns with Tasks

**GET** `/api/campaigns/`

Returns campaigns for a given account with their mapped tasks. Supports filtering tasks by user ownership. If pagination parameters (`page` or `page_size`) are provided, returns paginated results. Otherwise, returns all campaigns without pagination.

### Query Parameters

| Parameter   | Type   | Required | Default | Description                                      |
|------------|--------|----------|---------|--------------------------------------------------|
| `account_id`| string | Yes      | -       | Salesforce Account ID (required)                 |
| `user_id`  | string | No       | -       | Salesforce User ID (required when type='my')     |
| `type`     | string | No       | all     | Filter type: 'all' or 'my'                       |
| `page`     | int    | No       | -       | Page number (if provided, enables pagination)    |
| `page_size`| int    | No       | -       | Number of items per page (max: 100, if provided, enables pagination) |

### Type Parameter

- `all` (default): Returns all tasks mapped to each campaign
- `my`: Returns only tasks owned by the specified user (requires `user_id`)

### Response Fields

Each campaign object contains:

| Field       | Type    | Description                                    |
|------------|---------|------------------------------------------------|
| `id`       | string  | Campaign's Salesforce ID                       |
| `name`     | string  | Campaign name                                  |
| `status`   | string  | Campaign status                                |
| `type`     | string  | Campaign type                                  |
| `start_date`| date   | Campaign start date                            |
| `end_date` | date    | Campaign end date                              |
| `owner_id` | string  | Owner's Salesforce ID                          |
| `account_id`| string | Account's Salesforce ID                        |
| `is_active`| boolean | Whether campaign is active                     |
| `tasks`    | array   | Array of task objects                          |

Each task object contains:

| Field         | Type   | Description                                    |
|--------------|--------|------------------------------------------------|
| `id`         | string | Task's Salesforce ID                           |
| `subject`    | string | Task subject                                   |
| `status`     | string | Task status                                    |
| `priority`   | string | Task priority                                  |
| `activity_date`| date | Task activity date                             |
| `owner_id`   | string | Task owner's Salesforce ID                     |
| `campaign_id`| string | Campaign's Salesforce ID                       |
| `what_id`    | string | Related object ID                              |
| `what_type`  | string | Related object type                            |
| `what_name`  | string | Related object name                            |

### Example Requests

```bash
# Get all campaigns with all tasks (no pagination)
curl -s -X GET "http://localhost:8000/api/campaigns/?account_id=001xx000001234ABC"

# Get campaigns with only user's tasks (no pagination)
curl -s -X GET "http://localhost:8000/api/campaigns/?account_id=001xx000001234ABC&type=my&user_id=005xx000001234ABC"

# Get campaigns with pagination
curl -s -X GET "http://localhost:8000/api/campaigns/?account_id=001xx000001234ABC&page=1&page_size=10"

# Get campaigns with user filter and pagination
curl -s -X GET "http://localhost:8000/api/campaigns/?account_id=001xx000001234ABC&type=my&user_id=005xx000001234ABC&page=1"
```

### Success Response - All Data (200 OK)

When no pagination parameters are provided:

```json
{
  "success": true,
  "message": "Data retrieved successfully",
  "data": [
    {
      "id": "701xx000001234ABC",
      "name": "Summer Promotion 2024",
      "status": "In Progress",
      "type": "Email",
      "start_date": "2024-06-01",
      "end_date": "2024-08-31",
      "owner_id": "005xx000001234ABC",
      "account_id": "001xx000001234ABC",
      "is_active": true,
      "tasks": [
        {
          "id": "00Txx000001234ABC",
          "subject": "Send campaign emails",
          "status": "In Progress",
          "priority": "High",
          "activity_date": "2024-06-15",
          "owner_id": "005xx000001234ABC",
          "campaign_id": "701xx000001234ABC",
          "what_id": "701xx000001234ABC",
          "what_type": "Campaign",
          "what_name": "Summer Promotion 2024"
        }
      ]
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
      "id": "701xx000001234ABC",
      "name": "Summer Promotion 2024",
      "status": "In Progress",
      "type": "Email",
      "start_date": "2024-06-01",
      "end_date": "2024-08-31",
      "owner_id": "005xx000001234ABC",
      "account_id": "001xx000001234ABC",
      "is_active": true,
      "tasks": [
        {
          "id": "00Txx000001234ABC",
          "subject": "Send campaign emails",
          "status": "In Progress",
          "priority": "High",
          "activity_date": "2024-06-15",
          "owner_id": "005xx000001234ABC",
          "campaign_id": "701xx000001234ABC",
          "what_id": "701xx000001234ABC",
          "what_type": "Campaign",
          "what_name": "Summer Promotion 2024"
        }
      ]
    }
  ],
  "meta": {
    "pagination": {
      "current_page": 1,
      "page_size": 10,
      "total_count": 1,
      "total_pages": 1,
      "has_next": false,
      "has_previous": false
    }
  }
}
```

### Empty Result (200 OK)

When no campaigns are found:

```json
{
  "success": true,
  "message": "Data retrieved successfully",
  "data": []
}
```

### Validation Error (400 Bad Request)

When required parameters are missing or invalid:

```json
{
  "success": false,
  "message": "Invalid query parameters",
  "error_code": "VALIDATION_ERROR",
  "errors": [
    {
      "field": "account_id",
      "message": "account_id is required"
    }
  ]
}
```

---

## 2) List Tasks by Campaign

**GET** `/api/campaigns/tasks/`

Returns tasks mapped to a specific campaign. If pagination parameters (`page` or `page_size`) are provided, returns paginated results. Otherwise, returns all tasks without pagination.

### Query Parameters

| Parameter    | Type   | Required | Default | Description                                      |
|-------------|--------|----------|---------|--------------------------------------------------|
| `campaign_id`| string | Yes      | -       | Salesforce Campaign ID (required)                |
| `page`      | int    | No       | -       | Page number (if provided, enables pagination)    |
| `page_size` | int    | No       | -       | Number of items per page (max: 100, if provided, enables pagination) |

### Response Fields

Each task object contains the same fields as described in the campaigns endpoint.

### Example Requests

```bash
# Get all tasks for a campaign (no pagination)
curl -s -X GET "http://localhost:8000/api/campaigns/tasks/?campaign_id=701xx000001234ABC"

# Get tasks with pagination
curl -s -X GET "http://localhost:8000/api/campaigns/tasks/?campaign_id=701xx000001234ABC&page=1&page_size=20"
```

### Success Response - All Data (200 OK)

When no pagination parameters are provided:

```json
{
  "success": true,
  "message": "Data retrieved successfully",
  "data": [
    {
      "id": "00Txx000001234ABC",
      "subject": "Send campaign emails",
      "status": "In Progress",
      "priority": "High",
      "activity_date": "2024-06-15",
      "owner_id": "005xx000001234ABC",
      "campaign_id": "701xx000001234ABC",
      "what_id": "701xx000001234ABC",
      "what_type": "Campaign",
      "what_name": "Summer Promotion 2024"
    }
  ]
}
```

### Success Response - Paginated (200 OK)

When pagination parameters are provided:

```json
{
  "success": true,
  "message": "Data retrieved successfully",
  "data": [
    {
      "id": "00Txx000001234ABC",
      "subject": "Send campaign emails",
      "status": "In Progress",
      "priority": "High",
      "activity_date": "2024-06-15",
      "owner_id": "005xx000001234ABC",
      "campaign_id": "701xx000001234ABC",
      "what_id": "701xx000001234ABC",
      "what_type": "Campaign",
      "what_name": "Summer Promotion 2024"
    }
  ],
  "meta": {
    "pagination": {
      "current_page": 1,
      "page_size": 20,
      "total_count": 1,
      "total_pages": 1,
      "has_next": false,
      "has_previous": false
    }
  }
}
```

### Validation Error (400 Bad Request)

When campaign_id is missing:

```json
{
  "success": false,
  "message": "Invalid query parameters",
  "error_code": "VALIDATION_ERROR",
  "errors": [
    {
      "field": "campaign_id",
      "message": "campaign_id is required"
    }
  ]
}
```

---

## Error Responses

### 400 - Bad Request

Invalid or missing required parameters:

```json
{
  "success": false,
  "message": "Invalid query parameters",
  "error_code": "VALIDATION_ERROR",
  "errors": [
    {
      "field": "account_id",
      "message": "account_id is required"
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

- Campaigns are sorted alphabetically by name
- Tasks are sorted by activity date and subject
- Pagination is optional:
  - If `page` or `page_size` parameters are provided, the response will be paginated
  - If no pagination parameters are provided, all data is returned without pagination
  - Default page size when paginating is 20 items
  - Maximum page size is 100 items
- The `type` parameter controls task filtering:
  - `all`: Returns all tasks for each campaign
  - `my`: Returns only tasks owned by the specified user (requires `user_id`)
- All responses follow the project's standardized format with `success`, `message`, `data`, and optional `meta` or `errors` fields
- Error responses include `error_code` for programmatic error handling
- Swagger UI will show `page` and `page_size` as optional input parameters
