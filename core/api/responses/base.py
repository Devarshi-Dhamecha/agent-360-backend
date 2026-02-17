"""
Base Response Structure for Agent 360 API

Provides standardized response format for all API endpoints.
"""
from typing import Any, Optional, Dict, List
from rest_framework.response import Response
from rest_framework import status


class APIResponse:
    """
    Standardized API Response Format
    
    Success Response:
    {
        "success": true,
        "message": "Operation successful",
        "data": {...},
        "meta": {...}
    }
    
    Error Response:
    {
        "success": false,
        "message": "Error message",
        "errors": [...],
        "error_code": "ERROR_CODE"
    }
    """
    
    @staticmethod
    def success(
        data: Any = None,
        message: str = "Operation successful",
        status_code: int = status.HTTP_200_OK,
        meta: Optional[Dict] = None
    ) -> Response:
        """
        Return success response
        
        Args:
            data: Response data (dict, list, or any serializable object)
            message: Success message
            status_code: HTTP status code
            meta: Additional metadata (pagination, etc.)
            
        Returns:
            Response: DRF Response object
        """
        response_data = {
            "success": True,
            "message": message,
            "data": data if data is not None else {},
        }
        
        if meta:
            response_data["meta"] = meta
            
        return Response(response_data, status=status_code)
    
    @staticmethod
    def error(
        message: str = "An error occurred",
        errors: Optional[List[Dict[str, Any]]] = None,
        error_code: Optional[str] = None,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        data: Optional[Dict] = None
    ) -> Response:
        """
        Return error response
        
        Args:
            message: Error message
            errors: List of detailed errors
            error_code: Application-specific error code
            status_code: HTTP status code
            data: Additional error data
            
        Returns:
            Response: DRF Response object
        """
        response_data = {
            "success": False,
            "message": message,
        }
        
        if errors:
            response_data["errors"] = errors
        
        if error_code:
            response_data["error_code"] = error_code
            
        if data:
            response_data["data"] = data
            
        return Response(response_data, status=status_code)
    
    @staticmethod
    def created(
        data: Any = None,
        message: str = "Resource created successfully",
        resource_id: Optional[str] = None
    ) -> Response:
        """Return created response (201)"""
        meta = {"resource_id": resource_id} if resource_id else None
        return APIResponse.success(
            data=data,
            message=message,
            status_code=status.HTTP_201_CREATED,
            meta=meta
        )
    
    @staticmethod
    def updated(
        data: Any = None,
        message: str = "Resource updated successfully"
    ) -> Response:
        """Return updated response (200)"""
        return APIResponse.success(
            data=data,
            message=message,
            status_code=status.HTTP_200_OK
        )
    
    @staticmethod
    def deleted(
        message: str = "Resource deleted successfully"
    ) -> Response:
        """Return deleted response (200)"""
        return APIResponse.success(
            data=None,
            message=message,
            status_code=status.HTTP_200_OK
        )
    
    @staticmethod
    def no_content(
        message: str = "No content"
    ) -> Response:
        """Return no content response (204)"""
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @staticmethod
    def paginated(
        data: List[Any],
        page: int,
        page_size: int,
        total_count: int,
        message: str = "Data retrieved successfully"
    ) -> Response:
        """
        Return paginated response
        
        Args:
            data: List of items for current page
            page: Current page number
            page_size: Items per page
            total_count: Total number of items
            message: Success message
            
        Returns:
            Response: DRF Response object with pagination meta
        """
        total_pages = (total_count + page_size - 1) // page_size
        
        meta = {
            "pagination": {
                "current_page": page,
                "page_size": page_size,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1
            }
        }
        
        return APIResponse.success(
            data=data,
            message=message,
            meta=meta
        )
