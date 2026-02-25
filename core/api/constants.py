"""
API Constants

Global constants for error messages, validation messages, and success messages.
"""

# ============================================================================
# ERROR MESSAGES
# ============================================================================

class ErrorMessages:
    """Error message constants"""
    
    # General Errors
    BAD_REQUEST = "Bad request"
    UNAUTHORIZED = "Unauthorized access"
    FORBIDDEN = "Access forbidden"
    NOT_FOUND = "Resource not found"
    CONFLICT = "Resource conflict"
    VALIDATION_ERROR = "Validation error"
    VALIDATION_FAILED = "Validation failed"
    INTERNAL_ERROR = "Internal server error"
    SERVICE_UNAVAILABLE = "Service temporarily unavailable"
    
    # Authentication & Authorization
    INVALID_CREDENTIALS = "Invalid credentials"
    TOKEN_EXPIRED = "Token has expired"
    TOKEN_INVALID = "Invalid token"
    PERMISSION_DENIED = "Permission denied"
    
    # Resource Errors
    RESOURCE_NOT_FOUND = "Resource not found"
    ACCOUNT_NOT_FOUND = "Account not found"
    CASE_NOT_FOUND = "Case not found"
    DUPLICATE_RESOURCE = "Resource already exists"
    
    # Validation Errors
    REQUIRED_FIELD_MISSING = "Required fields missing"
    INVALID_QUERY_PARAMS = "Invalid query parameters"
    INVALID_REQUEST_BODY = "Invalid request body"
    INVALID_DATE_FORMAT = "Invalid date format"
    INVALID_DATE_RANGE = "Invalid date range"
    INVALID_PAGINATION_PARAMS = "Invalid pagination parameters"
    
    # Field-Specific Errors
    USER_ID_REQUIRED = "User ID is required"
    USER_ID_EMPTY = "User ID cannot be empty"
    ACCOUNT_ID_REQUIRED = "account_id is required"
    PRODUCT_IDS_REQUIRED = "At least one product_id is required"
    YEAR_REQUIRED = "year is required"
    YEAR_INVALID_FORMAT = "year must be an integer (e.g. 2026)"
    YEAR_OUT_OF_RANGE = "year must be between 2000 and 2100"
    FROM_MONTH_REQUIRED = "from (YYYY-MM) is required"
    TO_MONTH_REQUIRED = "to (YYYY-MM) is required"
    DATE_FORMAT_INVALID = "Invalid date. Use YYYY-MM-DD."
    MONTH_FORMAT_INVALID = "Must be YYYY-MM"
    END_DATE_BEFORE_START = "End date must be >= start date"
    END_MONTH_BEFORE_START = "End month must be on or after start month"
    
    # Status & Ordering Errors
    INVALID_STATUS = "Invalid status. Allowed: {allowed}"
    INVALID_ORDERING = "Invalid ordering. Allowed: {allowed}"
    
    # RFC/Update Errors
    ACCOUNT_ID_REQUIRED_BODY = "accountId is required"
    UPDATES_REQUIRED = "updates must be a non-empty array"
    UPDATES_MAX_EXCEEDED = "At most {max} items allowed per request"
    UPDATES_INVALID_ITEM = "Each item must have productId, month, draftRfcQty"
    UPDATES_DUPLICATE = "Duplicate productId and month in updates"
    PRODUCTS_NOT_FOUND = "Product(s) not found: {products}"
    DRAFT_RFC_QTY_REQUIRED = "draftRfcQty is required"
    ONLY_FUTURE_MONTHS = "Only future months can be edited"
    JSON_BODY_REQUIRED = "JSON body with accountId and updates is required"
    
    # Query Parameter Errors
    QUERY_PARAM_REQUIRED = "This query parameter is required."
    
    # Email Validation
    INVALID_EMAIL = "Invalid email address"
    
    # Pagination
    PAGE_SIZE_INVALID = "Must be valid integers"


# ============================================================================
# SUCCESS MESSAGES
# ============================================================================

class SuccessMessages:
    """Success message constants"""
    
    # General
    DATA_RETRIEVED = "Data retrieved successfully"
    
    # Accounts
    ACCOUNTS_RETRIEVED = "Data retrieved successfully"
    
    # Cases
    SUMMARY_RETRIEVED = "Summary retrieved successfully"
    CASE_RETRIEVED = "Case retrieved successfully"
    COMMENTS_RETRIEVED = "Comments retrieved successfully"
    COMMENT_CREATED = "Comment created successfully"
    TIMELINE_RETRIEVED = "Timeline retrieved successfully"
    
    # Products
    QUARTERLY_PERFORMANCE_RETRIEVED = "Achieved (by quarter or year) retrieved successfully"
    PRODUCT_PERFORMANCE_RETRIEVED = "Product performance data retrieved successfully"
    RFC_BY_MONTH_RETRIEVED = "RFC by month retrieved successfully"
    RFC_UPDATED = "RFC updated successfully"
    PRODUCT_FAMILY_ANALYTICS_RETRIEVED = "Product family analytics retrieved successfully"
    SALES_ANALYTICS_RETRIEVED = "Sales analytics retrieved successfully"


# ============================================================================
# ERROR CODES
# ============================================================================

class ErrorCodes:
    """Error code constants"""
    
    # General
    BAD_REQUEST = "BAD_REQUEST"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    
    # Authentication
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_INVALID = "TOKEN_INVALID"
    
    # Authorization
    PERMISSION_DENIED = "PERMISSION_DENIED"
    
    # Resources
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    DUPLICATE_RESOURCE = "DUPLICATE_RESOURCE"
    
    # Validation
    REQUIRED_FIELD_MISSING = "REQUIRED_FIELD_MISSING"
    INVALID_FIELD = "INVALID_FIELD"
    INVALID_PARAMETER = "INVALID_PARAMETER"
    MISSING_PARAMETER = "MISSING_PARAMETER"
    
    # Business Logic
    BUSINESS_LOGIC_ERROR = "BUSINESS_LOGIC_ERROR"
    INSUFFICIENT_BALANCE = "INSUFFICIENT_BALANCE"
    QUOTA_EXCEEDED = "QUOTA_EXCEEDED"
    
    # Database
    DATABASE_ERROR = "DATABASE_ERROR"
    
    # Custom
    PERFORMANCE_CALCULATION_ERROR = "PERFORMANCE_CALCULATION_ERROR"


# ============================================================================
# FIELD NAMES
# ============================================================================

class FieldNames:
    """Field name constants for error messages"""
    
    USER_ID = "user_id"
    ACCOUNT_ID = "account_id"
    PRODUCT_ID = "productId"
    PRODUCT_IDS = "product_ids"
    YEAR = "year"
    FROM = "from"
    TO = "to"
    FROM_TO = "from/to"
    STATUS = "status"
    ORDERING = "ordering"
    PAGE = "page"
    PAGE_SIZE = "page_size"
    BODY = "body"
    UPDATES = "updates"
    COMMENT_BODY = "comment_body"
    CREATED_BY_ID = "created_by_id"
    OPENED_FROM = "opened_from"
    OPENED_TO = "opened_to"


# ============================================================================
# VALIDATION CONSTANTS
# ============================================================================

class ValidationConstants:
    """Validation-related constants"""
    
    # Year validation
    MIN_YEAR = 2000
    MAX_YEAR = 2100
    
    # Date formats
    DATE_FORMAT = "%Y-%m-%d"
    MONTH_FORMAT = "%Y-%m"
    
    # Pagination
    MAX_PAGE_SIZE = 100
    DEFAULT_PAGE_SIZE = 20
    
    # RFC Updates
    MAX_RFC_UPDATES = 100
    
    # Status choices
    STATUS_OPEN = "open"
    STATUS_CLOSED = "closed"
    STATUS_ALL = "all"
    STATUS_CHOICES = (STATUS_OPEN, STATUS_CLOSED, STATUS_ALL)
    
    # Ordering choices
    ORDERING_OPENED_AT = "opened_at"
    ORDERING_OPENED_AT_DESC = "-opened_at"
    ORDERING_LAST_MODIFIED = "last_modified"
    ORDERING_LAST_MODIFIED_DESC = "-last_modified"
