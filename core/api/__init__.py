"""
Core API Module

Provides standardized request/response handling, exceptions, and utilities.
"""
from .responses import APIResponse, SuccessResponse, ErrorResponse
from .exceptions import (
    BaseAPIException,
    InvalidCredentialsException,
    TokenExpiredException,
    UnauthorizedException,
    PermissionDeniedException,
    ResourceNotFoundException,
    ValidationException,
    custom_exception_handler,
)
from .serializers import (
    BaseRequestSerializer,
    BaseResponseSerializer,
    BaseModelSerializer,
    ListRequestSerializer,
)
from .utils import StandardPagination

__all__ = [
    'APIResponse',
    'SuccessResponse',
    'ErrorResponse',
    'BaseAPIException',
    'InvalidCredentialsException',
    'TokenExpiredException',
    'UnauthorizedException',
    'PermissionDeniedException',
    'ResourceNotFoundException',
    'ValidationException',
    'custom_exception_handler',
    'BaseRequestSerializer',
    'BaseResponseSerializer',
    'BaseModelSerializer',
    'ListRequestSerializer',
    'StandardPagination',
]
