"""
Error Response Handlers

Provides convenient error response methods for common error scenarios.
"""
from typing import Any, Optional, List, Dict
from rest_framework import status
from .base import APIResponse


class ErrorResponse:
    """Convenience class for error responses"""
    
    @staticmethod
    def bad_request(
        message: str = "Bad request",
        errors: Optional[List[Dict]] = None,
        error_code: str = "BAD_REQUEST"
    ) -> Any:
        """400 - Bad Request"""
        return APIResponse.error(
            message=message,
            errors=errors,
            error_code=error_code,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    @staticmethod
    def unauthorized(
        message: str = "Unauthorized access",
        error_code: str = "UNAUTHORIZED"
    ) -> Any:
        """401 - Unauthorized"""
        return APIResponse.error(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    @staticmethod
    def forbidden(
        message: str = "Access forbidden",
        error_code: str = "FORBIDDEN"
    ) -> Any:
        """403 - Forbidden"""
        return APIResponse.error(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    @staticmethod
    def not_found(
        message: str = "Resource not found",
        error_code: str = "NOT_FOUND",
        resource_type: Optional[str] = None
    ) -> Any:
        """404 - Not Found"""
        data = {"resource_type": resource_type} if resource_type else None
        return APIResponse.error(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_404_NOT_FOUND,
            data=data
        )
    
    @staticmethod
    def conflict(
        message: str = "Resource conflict",
        error_code: str = "CONFLICT",
        errors: Optional[List[Dict]] = None
    ) -> Any:
        """409 - Conflict"""
        return APIResponse.error(
            message=message,
            errors=errors,
            error_code=error_code,
            status_code=status.HTTP_409_CONFLICT
        )
    
    @staticmethod
    def validation_error(
        message: str = "Validation error",
        errors: Optional[List[Dict]] = None,
        error_code: str = "VALIDATION_ERROR"
    ) -> Any:
        """422 - Validation Error"""
        return APIResponse.error(
            message=message,
            errors=errors,
            error_code=error_code,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    
    @staticmethod
    def server_error(
        message: str = "Internal server error",
        error_code: str = "INTERNAL_ERROR"
    ) -> Any:
        """500 - Internal Server Error"""
        return APIResponse.error(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    @staticmethod
    def service_unavailable(
        message: str = "Service temporarily unavailable",
        error_code: str = "SERVICE_UNAVAILABLE"
    ) -> Any:
        """503 - Service Unavailable"""
        return APIResponse.error(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    @staticmethod
    def custom(
        message: str,
        status_code: int,
        error_code: Optional[str] = None,
        errors: Optional[List[Dict]] = None
    ) -> Any:
        """Custom error response"""
        return APIResponse.error(
            message=message,
            errors=errors,
            error_code=error_code,
            status_code=status_code
        )
    
    # Authentication & Authorization Errors
    
    @staticmethod
    def invalid_credentials(message: str = "Invalid credentials") -> Any:
        """Invalid login credentials"""
        return ErrorResponse.unauthorized(
            message=message,
            error_code="INVALID_CREDENTIALS"
        )
    
    @staticmethod
    def token_expired(message: str = "Token has expired") -> Any:
        """Expired authentication token"""
        return ErrorResponse.unauthorized(
            message=message,
            error_code="TOKEN_EXPIRED"
        )
    
    @staticmethod
    def token_invalid(message: str = "Invalid token") -> Any:
        """Invalid authentication token"""
        return ErrorResponse.unauthorized(
            message=message,
            error_code="TOKEN_INVALID"
        )
    
    @staticmethod
    def permission_denied(message: str = "Permission denied") -> Any:
        """Permission denied"""
        return ErrorResponse.forbidden(
            message=message,
            error_code="PERMISSION_DENIED"
        )
    
    # Resource Errors
    
    @staticmethod
    def resource_not_found(resource_type: str, resource_id: Optional[str] = None) -> Any:
        """Specific resource not found"""
        message = f"{resource_type} not found"
        if resource_id:
            message = f"{resource_type} with ID '{resource_id}' not found"
        return ErrorResponse.not_found(
            message=message,
            error_code="RESOURCE_NOT_FOUND",
            resource_type=resource_type
        )
    
    @staticmethod
    def duplicate_resource(
        message: str = "Resource already exists",
        field: Optional[str] = None
    ) -> Any:
        """Duplicate resource"""
        errors = [{"field": field, "message": f"Duplicate value for {field}"}] if field else None
        return ErrorResponse.conflict(
            message=message,
            error_code="DUPLICATE_RESOURCE",
            errors=errors
        )
    
    @staticmethod
    def required_field_missing(fields: List[str]) -> Any:
        """Required fields missing"""
        errors = [{"field": field, "message": f"{field} is required"} for field in fields]
        return ErrorResponse.validation_error(
            message="Required fields missing",
            error_code="REQUIRED_FIELD_MISSING",
            errors=errors
        )
