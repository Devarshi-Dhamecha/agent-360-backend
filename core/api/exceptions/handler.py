"""
Custom Exception Handler

Handles all exceptions and returns standardized error responses.
"""
from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError, NotAuthenticated, PermissionDenied
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from rest_framework import status
import logging

from ..responses import ErrorResponse

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF
    
    This handler catches all exceptions and returns standardized error responses.
    """
    
    # Call DRF's default exception handler first
    response = exception_handler(exc, context)
    
    # Log the exception
    view = context.get('view', None)
    request = context.get('request', None)
    
    if view and request:
        logger.error(
            f"Exception in {view.__class__.__name__}: {str(exc)}",
            exc_info=True,
            extra={
                'view': view.__class__.__name__,
                'method': request.method,
                'path': request.path,
                'user': str(request.user) if hasattr(request, 'user') else 'Anonymous'
            }
        )
    
    # Handle custom API exceptions
    if hasattr(exc, 'error_code'):
        return ErrorResponse.custom(
            message=str(exc.detail) if hasattr(exc, 'detail') else str(exc),
            status_code=exc.status_code if hasattr(exc, 'status_code') else status.HTTP_400_BAD_REQUEST,
            error_code=exc.error_code
        )
    
    # Handle DRF ValidationError
    if isinstance(exc, ValidationError):
        errors = []
        if isinstance(exc.detail, dict):
            for field, messages in exc.detail.items():
                if isinstance(messages, list):
                    for message in messages:
                        errors.append({
                            "field": field,
                            "message": str(message)
                        })
                else:
                    errors.append({
                        "field": field,
                        "message": str(messages)
                    })
        elif isinstance(exc.detail, list):
            for message in exc.detail:
                errors.append({
                    "field": "non_field_errors",
                    "message": str(message)
                })
        else:
            errors.append({
                "field": "non_field_errors",
                "message": str(exc.detail)
            })
        
        return ErrorResponse.validation_error(
            message="Validation failed",
            errors=errors
        )
    
    # Handle authentication errors
    if isinstance(exc, NotAuthenticated):
        return ErrorResponse.unauthorized(
            message=str(exc.detail) if hasattr(exc, 'detail') else "Authentication required"
        )
    
    # Handle permission errors
    if isinstance(exc, PermissionDenied):
        return ErrorResponse.forbidden(
            message=str(exc.detail) if hasattr(exc, 'detail') else "Permission denied"
        )
    
    # Handle 404 errors
    if isinstance(exc, (Http404, ObjectDoesNotExist)):
        return ErrorResponse.not_found(
            message=str(exc) if str(exc) else "Resource not found"
        )
    
    # Handle other DRF exceptions
    if response is not None:
        error_message = "An error occurred"
        
        if hasattr(exc, 'detail'):
            if isinstance(exc.detail, dict):
                error_message = str(next(iter(exc.detail.values())))
            elif isinstance(exc.detail, list):
                error_message = str(exc.detail[0]) if exc.detail else error_message
            else:
                error_message = str(exc.detail)
        
        return ErrorResponse.custom(
            message=error_message,
            status_code=response.status_code,
            error_code=exc.__class__.__name__.upper()
        )
    
    # Handle unexpected errors (500)
    logger.critical(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return ErrorResponse.server_error(
        message="An unexpected error occurred. Please try again later."
    )


def format_validation_errors(errors):
    """
    Format validation errors into a list of dicts
    
    Args:
        errors: ValidationError detail
        
    Returns:
        List of error dicts with field and message
    """
    formatted_errors = []
    
    if isinstance(errors, dict):
        for field, messages in errors.items():
            if isinstance(messages, list):
                for message in messages:
                    formatted_errors.append({
                        "field": field,
                        "message": str(message)
                    })
            else:
                formatted_errors.append({
                    "field": field,
                    "message": str(messages)
                })
    elif isinstance(errors, list):
        for message in errors:
            formatted_errors.append({
                "field": "non_field_errors",
                "message": str(message)
            })
    else:
        formatted_errors.append({
            "field": "non_field_errors",
            "message": str(errors)
        })
    
    return formatted_errors
