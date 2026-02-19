# Accounts API

Base URL: `/api/accounts/`  
Auth: `AllowAny` (no authentication required).

---

## List accounts (with optional filter by User ID)

**GET** `/api/accounts/`

Returns accounts, optionally filtered by owner (user) Salesforce ID.

**Query params:**

| Param      | Type   | Description                                      |
|-----------|--------|--------------------------------------------------|
| `user_id` | string | Optional. Filter accounts by owner (User SF id). |
| `page`    | int    | Page number (default 1).                         |
| `page_size` | int  | Page size (default 20, max 100).                 |

**Example – all accounts:**
```bash
curl -s -X GET "http://localhost:8000/api/accounts/"
```

**Example – accounts for a specific user (owner):**
```bash
curl -s -X GET "http://localhost:8000/api/accounts/?user_id=005xx000001234ABC"
```

**Response (200):**
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
    }
  ],
  "meta": {
    "page": 1,
    "page_size": 20,
    "total_count": 1
  }
}
```
