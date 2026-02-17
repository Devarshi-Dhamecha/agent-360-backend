"""
Success Response Handlers

Provides convenient success response methods for common operations.
"""
from typing import Any, Optional, Dict
from rest_framework import status
from .base import APIResponse


class SuccessResponse:
    """Convenience class for success responses"""
    
    @staticmethod
    def retrieve(data: Any, message: str = "Resource retrieved successfully") -> Any:
        """GET - Single resource retrieved"""
        return APIResponse.success(
            data=data,
            message=message,
            status_code=status.HTTP_200_OK
        )
    
    @staticmethod
    def list(data: list, message: str = "Resources retrieved successfully", meta: Optional[Dict] = None) -> Any:
        """GET - List of resources retrieved"""
        return APIResponse.success(
            data=data,
            message=message,
            status_code=status.HTTP_200_OK,
            meta=meta
        )
    
    @staticmethod
    def create(data: Any, message: str = "Resource created successfully", resource_id: Optional[str] = None) -> Any:
        """POST - Resource created"""
        return APIResponse.created(
            data=data,
            message=message,
            resource_id=resource_id
        )
    
    @staticmethod
    def update(data: Any, message: str = "Resource updated successfully") -> Any:
        """PUT/PATCH - Resource updated"""
        return APIResponse.updated(
            data=data,
            message=message
        )
    
    @staticmethod
    def delete(message: str = "Resource deleted successfully") -> Any:
        """DELETE - Resource deleted"""
        return APIResponse.deleted(message=message)
    
    @staticmethod
    def custom(data: Any = None, message: str = "Operation completed", status_code: int = status.HTTP_200_OK) -> Any:
        """Custom success response"""
        return APIResponse.success(
            data=data,
            message=message,
            status_code=status_code
        )
    
    @staticmethod
    def login(data: Dict, message: str = "Login successful") -> Any:
        """Login success response"""
        return APIResponse.success(
            data=data,
            message=message,
            status_code=status.HTTP_200_OK
        )
    
    @staticmethod
    def logout(message: str = "Logout successful") -> Any:
        """Logout success response"""
        return APIResponse.success(
            data=None,
            message=message,
            status_code=status.HTTP_200_OK
        )
    
    @staticmethod
    def register(data: Dict, message: str = "Registration successful") -> Any:
        """Registration success response"""
        return APIResponse.created(
            data=data,
            message=message
        )
    
    @staticmethod
    def password_reset(message: str = "Password reset email sent") -> Any:
        """Password reset request success"""
        return APIResponse.success(
            data=None,
            message=message,
            status_code=status.HTTP_200_OK
        )
    
    @staticmethod
    def password_change(message: str = "Password changed successfully") -> Any:
        """Password change success"""
        return APIResponse.success(
            data=None,
            message=message,
            status_code=status.HTTP_200_OK
        )
