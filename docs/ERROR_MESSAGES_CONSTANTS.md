# Error Messages Constants

This document explains how to use the global constants for error messages, success messages, and validation constants in the API.

## Overview

All error messages, success messages, error codes, field names, and validation constants are centralized in `core/api/constants.py`. This ensures consistency across the codebase and makes it easy to update messages in one place.

## Available Constants

### ErrorMessages

Contains all error message strings used throughout the application.

```python
from core.api.constants import ErrorMessages

# General errors
ErrorMessages.BAD_REQUEST
ErrorMessages.UNAUTHORIZED
ErrorMessages.NOT_FOUND
ErrorMessages.VALIDATION_ERROR

# Field-specific errors
ErrorMessages.USER_ID_REQUIRED
ErrorMessages.USER_ID_EMPTY
ErrorMessages.ACCOUNT_ID_REQUIRED
ErrorMessages.PRODUCT_IDS_REQUIRED

# Date/time errors
ErrorMessages.INVALID_DATE_FORMAT
ErrorMessages.INVALID_DATE_RANGE
ErrorMessages.END_DATE_BEFORE_START
```

### SuccessMessages

Contains all success message strings.

```python
from core.api.constants import SuccessMessages

SuccessMessages.DATA_RETRIEVED
SuccessMessages.CASE_RETRIEVED
SuccessMessages.COMMENT_CREATED
SuccessMessages.RFC_UPDATED
```

### ErrorCodes

Contains all error code constants.

```python
from core.api.constants import ErrorCodes

ErrorCodes.BAD_REQUEST
ErrorCodes.VALIDATION_ERROR
ErrorCodes.REQUIRED_FIELD_MISSING
ErrorCodes.PERFORMANCE_CALCULATION_ERROR
```

### FieldNames

Contains all field name constants for error messages.

```python
from core.api.constants import FieldNames

FieldNames.USER_ID
FieldNames.ACCOUNT_ID
FieldNames.PRODUCT_IDS
FieldNames.FROM
FieldNames.TO
```

### ValidationConstants

Contains validation-related constants like limits, formats, and choices.

```python
from core.api.constants import ValidationConstants

# Limits
ValidationConstants.MIN_YEAR  # 2000
ValidationConstants.MAX_YEAR  # 2100
ValidationConstants.MAX_PAGE_SIZE  # 100
ValidationConstants.MAX_RFC_UPDATES  # 100

# Formats
ValidationConstants.DATE_FORMAT  # "%Y-%m-%d"
ValidationConstants.MONTH_FORMAT  # "%Y-%m"

# Choices
ValidationConstants.STATUS_CHOICES  # ('open', 'closed', 'all')
```

## Usage Examples

### In Views

```python
from core.api.responses import APIResponse, ErrorResponse
from core.api.constants import (
    ErrorMessages, SuccessMessages, ErrorCodes, FieldNames, ValidationConstants
)

class MyAPIView(APIView):
    def get(self, request):
        account_id = request.query_params.get('account_id')
        
        # Validation with constants
        if not account_id:
            return ErrorResponse.validation_error(
                message=ErrorMessages.INVALID_QUERY_PARAMS,
                errors=[{
                    "field": FieldNames.ACCOUNT_ID, 
                    "message": ErrorMessages.ACCOUNT_ID_REQUIRED
                }],
            )
        
        # Success response with constants
        return APIResponse.success(
            data=data,
            message=SuccessMessages.DATA_RETRIEVED
        )
```

### In Serializers

```python
from rest_framework import serializers
from core.api.constants import ErrorMessages, ValidationConstants

class MySerializer(serializers.Serializer):
    year = serializers.IntegerField()
    
    def validate_year(self, value):
        if value < ValidationConstants.MIN_YEAR or value > ValidationConstants.MAX_YEAR:
            raise serializers.ValidationError(ErrorMessages.YEAR_OUT_OF_RANGE)
        return value
```

### In Validators

```python
from rest_framework import serializers
from core.api.constants import ErrorMessages

def validate_email(value):
    try:
        django_validate_email(value)
    except DjangoValidationError:
        raise serializers.ValidationError(ErrorMessages.INVALID_EMAIL)
    return value
```

### With String Formatting

Some error messages support string formatting:

```python
# Messages with placeholders
ErrorMessages.INVALID_STATUS.format(allowed="open, closed, all")
ErrorMessages.PRODUCTS_NOT_FOUND.format(products="PRD-001, PRD-002")
ErrorMessages.UPDATES_MAX_EXCEEDED.format(max=100)
```

## Benefits

1. **Consistency**: All error messages are consistent across the application
2. **Maintainability**: Update messages in one place
3. **Type Safety**: IDE autocomplete helps prevent typos
4. **Internationalization Ready**: Easy to add i18n support later
5. **Documentation**: Clear overview of all messages in one file
6. **Testing**: Easy to test for specific error messages

## Migration Guide

If you have existing hardcoded strings, replace them with constants:

### Before
```python
if not user_id:
    return ErrorResponse.bad_request(
        message="User ID is required",
        errors=[{"field": "user_id", "message": "User ID cannot be empty"}],
        error_code="REQUIRED_FIELD_MISSING"
    )
```

### After
```python
if not user_id:
    return ErrorResponse.bad_request(
        message=ErrorMessages.USER_ID_REQUIRED,
        errors=[{"field": FieldNames.USER_ID, "message": ErrorMessages.USER_ID_EMPTY}],
        error_code=ErrorCodes.REQUIRED_FIELD_MISSING
    )
```

## Adding New Constants

When adding new error messages:

1. Add the constant to the appropriate class in `core/api/constants.py`
2. Use UPPER_SNAKE_CASE for constant names
3. Use clear, descriptive names
4. Group related constants together
5. Add comments for complex constants

Example:
```python
class ErrorMessages:
    # ... existing constants ...
    
    # New feature errors
    NEW_FEATURE_ERROR = "New feature error message"
    NEW_FEATURE_INVALID = "Invalid new feature value"
```
