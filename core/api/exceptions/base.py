"""
Custom API Exceptions

Provides custom exception classes for API error handling.
"""
from rest_framework.exceptions import APIException
from rest_framework import status


class BaseAPIException(APIException):
    """Base exception for all custom API exceptions"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "An error occurred"
    error_code = "API_ERROR"
    
    def __init__(self, detail=None, error_code=None, status_code=None):
        if detail is not None:
            self.detail = detail
        if error_code is not None:
            self.error_code = error_code
        if status_code is not None:
            self.status_code = status_code
        super().__init__(detail)


# Authentication Exceptions

class InvalidCredentialsException(BaseAPIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Invalid credentials provided"
    error_code = "INVALID_CREDENTIALS"


class TokenExpiredException(BaseAPIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Authentication token has expired"
    error_code = "TOKEN_EXPIRED"


class TokenInvalidException(BaseAPIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Invalid authentication token"
    error_code = "TOKEN_INVALID"


class UnauthorizedException(BaseAPIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Unauthorized access"
    error_code = "UNAUTHORIZED"


# Authorization Exceptions

class PermissionDeniedException(BaseAPIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "You do not have permission to perform this action"
    error_code = "PERMISSION_DENIED"


class ForbiddenException(BaseAPIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Access forbidden"
    error_code = "FORBIDDEN"


# Resource Exceptions

class ResourceNotFoundException(BaseAPIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Resource not found"
    error_code = "RESOURCE_NOT_FOUND"
    
    def __init__(self, resource_type=None, resource_id=None, detail=None):
        if detail is None and resource_type:
            if resource_id:
                detail = f"{resource_type} with ID '{resource_id}' not found"
            else:
                detail = f"{resource_type} not found"
        super().__init__(detail=detail)


class DuplicateResourceException(BaseAPIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Resource already exists"
    error_code = "DUPLICATE_RESOURCE"


class ResourceConflictException(BaseAPIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Resource conflict occurred"
    error_code = "RESOURCE_CONFLICT"


# Validation Exceptions

class ValidationException(BaseAPIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = "Validation error"
    error_code = "VALIDATION_ERROR"


class RequiredFieldException(BaseAPIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = "Required field missing"
    error_code = "REQUIRED_FIELD_MISSING"
    
    def __init__(self, field_name=None, detail=None):
        if detail is None and field_name:
            detail = f"Field '{field_name}' is required"
        super().__init__(detail=detail)


class InvalidFieldException(BaseAPIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = "Invalid field value"
    error_code = "INVALID_FIELD"
    
    def __init__(self, field_name=None, detail=None):
        if detail is None and field_name:
            detail = f"Invalid value for field '{field_name}'"
        super().__init__(detail=detail)


# Business Logic Exceptions

class BusinessLogicException(BaseAPIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = "Business logic error"
    error_code = "BUSINESS_LOGIC_ERROR"


class InsufficientBalanceException(BaseAPIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = "Insufficient balance"
    error_code = "INSUFFICIENT_BALANCE"


class QuotaExceededException(BaseAPIException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = "Quota exceeded"
    error_code = "QUOTA_EXCEEDED"


# Server Exceptions

class InternalServerException(BaseAPIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Internal server error occurred"
    error_code = "INTERNAL_ERROR"


class ServiceUnavailableException(BaseAPIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = "Service temporarily unavailable"
    error_code = "SERVICE_UNAVAILABLE"


class DatabaseException(BaseAPIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Database error occurred"
    error_code = "DATABASE_ERROR"


# Request Exceptions

class BadRequestException(BaseAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Bad request"
    error_code = "BAD_REQUEST"


class InvalidParameterException(BaseAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid parameter"
    error_code = "INVALID_PARAMETER"


class MissingParameterException(BaseAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Missing required parameter"
    error_code = "MISSING_PARAMETER"
