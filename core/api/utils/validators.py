"""
Custom Validators

Provides custom validation functions for API requests.
"""
from rest_framework import serializers
from django.core.validators import validate_email as django_validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
import re


def validate_salesforce_id(value):
    """
    Validate Salesforce-style ID (18 characters)
    
    Args:
        value: ID string to validate
        
    Raises:
        serializers.ValidationError: If ID is invalid
    """
    if not value:
        return value
    
    if not isinstance(value, str):
        raise serializers.ValidationError("ID must be a string")
    
    if len(value) != 18:
        raise serializers.ValidationError("ID must be exactly 18 characters")
    
    if not re.match(r'^[a-zA-Z0-9]{18}$', value):
        raise serializers.ValidationError("ID must contain only alphanumeric characters")
    
    return value


def validate_email(value):
    """
    Validate email address
    
    Args:
        value: Email string to validate
        
    Raises:
        serializers.ValidationError: If email is invalid
    """
    try:
        django_validate_email(value)
    except DjangoValidationError:
        raise serializers.ValidationError("Invalid email address")
    return value


def validate_phone_number(value):
    """
    Validate phone number (basic validation)
    
    Args:
        value: Phone number string to validate
        
    Raises:
        serializers.ValidationError: If phone number is invalid
    """
    if not value:
        return value
    
    # Remove common formatting characters
    cleaned = re.sub(r'[\s\-\(\)\+]', '', value)
    
    if not cleaned.isdigit():
        raise serializers.ValidationError("Phone number must contain only digits")
    
    if len(cleaned) < 10 or len(cleaned) > 15:
        raise serializers.ValidationError("Phone number must be between 10 and 15 digits")
    
    return value


def validate_positive_number(value):
    """
    Validate positive number
    
    Args:
        value: Number to validate
        
    Raises:
        serializers.ValidationError: If number is not positive
    """
    if value is not None and value <= 0:
        raise serializers.ValidationError("Value must be positive")
    return value


def validate_non_negative_number(value):
    """
    Validate non-negative number
    
    Args:
        value: Number to validate
        
    Raises:
        serializers.ValidationError: If number is negative
    """
    if value is not None and value < 0:
        raise serializers.ValidationError("Value must not be negative")
    return value


def validate_date_range(start_date, end_date):
    """
    Validate that end_date is after start_date
    
    Args:
        start_date: Start date
        end_date: End date
        
    Raises:
        serializers.ValidationError: If date range is invalid
    """
    if start_date and end_date and end_date < start_date:
        raise serializers.ValidationError("End date must be after start date")
    return True


def validate_currency_code(value):
    """
    Validate ISO currency code (3 letters)
    
    Args:
        value: Currency code to validate
        
    Raises:
        serializers.ValidationError: If currency code is invalid
    """
    if not value:
        return value
    
    if not isinstance(value, str) or len(value) != 3:
        raise serializers.ValidationError("Currency code must be 3 letters")
    
    if not value.isupper():
        raise serializers.ValidationError("Currency code must be uppercase")
    
    return value


def validate_percentage(value):
    """
    Validate percentage (0-100)
    
    Args:
        value: Percentage value to validate
        
    Raises:
        serializers.ValidationError: If percentage is invalid
    """
    if value is not None and (value < 0 or value > 100):
        raise serializers.ValidationError("Percentage must be between 0 and 100")
    return value


def validate_status_transition(current_status, new_status, allowed_transitions):
    """
    Validate status transition
    
    Args:
        current_status: Current status
        new_status: New status
        allowed_transitions: Dict of allowed transitions {status: [allowed_next_statuses]}
        
    Raises:
        serializers.ValidationError: If transition is not allowed
    """
    if current_status == new_status:
        return True
    
    if current_status not in allowed_transitions:
        raise serializers.ValidationError(f"Invalid current status: {current_status}")
    
    if new_status not in allowed_transitions[current_status]:
        raise serializers.ValidationError(
            f"Cannot transition from {current_status} to {new_status}"
        )
    
    return True
