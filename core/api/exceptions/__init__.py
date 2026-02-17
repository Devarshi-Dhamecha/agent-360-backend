"""
API Exceptions Module

Provides custom exception classes and handlers for API error handling.
"""
from .base import (
    BaseAPIException,
    InvalidCredentialsException,
    TokenExpiredException,
    TokenInvalidException,
    UnauthorizedException,
    PermissionDeniedException,
    ForbiddenException,
    ResourceNotFoundException,
    DuplicateResourceException,
    ResourceConflictException,
    ValidationException,
    RequiredFieldException,
    InvalidFieldException,
    BusinessLogicException,
    InsufficientBalanceException,
    QuotaExceededException,
    InternalServerException,
    ServiceUnavailableException,
    DatabaseException,
    BadRequestException,
    InvalidParameterException,
    MissingParameterException,
)
from .handler import custom_exception_handler

__all__ = [
    'BaseAPIException',
    'InvalidCredentialsException',
    'TokenExpiredException',
    'TokenInvalidException',
    'UnauthorizedException',
    'PermissionDeniedException',
    'ForbiddenException',
    'ResourceNotFoundException',
    'DuplicateResourceException',
    'ResourceConflictException',
    'ValidationException',
    'RequiredFieldException',
    'InvalidFieldException',
    'BusinessLogicException',
    'InsufficientBalanceException',
    'QuotaExceededException',
    'InternalServerException',
    'ServiceUnavailableException',
    'DatabaseException',
    'BadRequestException',
    'InvalidParameterException',
    'MissingParameterException',
    'custom_exception_handler',
]
