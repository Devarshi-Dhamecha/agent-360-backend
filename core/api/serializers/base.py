"""
Base Serializers

Provides base serializer classes with common functionality.
"""
from rest_framework import serializers
from typing import Dict, Any


class BaseRequestSerializer(serializers.Serializer):
    """
    Base serializer for API requests
    
    Provides common validation and error handling for request data.
    """
    
    def validate(self, attrs):
        """Override to add custom validation logic"""
        return super().validate(attrs)
    
    def to_internal_value(self, data):
        """Convert incoming request data to validated Python objects"""
        return super().to_internal_value(data)


class BaseResponseSerializer(serializers.Serializer):
    """
    Base serializer for API responses
    
    Provides common fields and formatting for response data.
    """
    
    def to_representation(self, instance):
        """Convert model instance to JSON-serializable format"""
        return super().to_representation(instance)


class BaseModelSerializer(serializers.ModelSerializer):
    """
    Base model serializer with common fields and methods
    
    Automatically includes audit fields and provides helper methods.
    """
    
    class Meta:
        abstract = True
        read_only_fields = ['id', 'created_date', 'last_modified_date']
    
    def get_user_display(self, user) -> Dict[str, Any]:
        """Helper method to format user data"""
        if not user:
            return None
        return {
            "id": user.id,
            "username": user.username,
            "name": user.name,
            "email": user.email
        }
    
    def validate(self, attrs):
        """Override to add custom validation logic"""
        return super().validate(attrs)


class TimestampedSerializer(serializers.Serializer):
    """Mixin for serializers that include timestamp fields"""
    created_date = serializers.DateTimeField(read_only=True)
    last_modified_date = serializers.DateTimeField(read_only=True)


class AuditedSerializer(TimestampedSerializer):
    """Mixin for serializers that include audit fields"""
    created_by = serializers.SerializerMethodField()
    last_modified_by = serializers.SerializerMethodField()
    
    def get_created_by(self, obj):
        """Get created by user details"""
        if not hasattr(obj, 'created_by') or not obj.created_by:
            return None
        return {
            "id": obj.created_by.id,
            "username": obj.created_by.username,
            "name": obj.created_by.name
        }
    
    def get_last_modified_by(self, obj):
        """Get last modified by user details"""
        if not hasattr(obj, 'last_modified_by') or not obj.last_modified_by:
            return None
        return {
            "id": obj.last_modified_by.id,
            "username": obj.last_modified_by.username,
            "name": obj.last_modified_by.name
        }


class PaginationSerializer(serializers.Serializer):
    """Serializer for pagination metadata"""
    current_page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total_count = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    has_next = serializers.BooleanField()
    has_previous = serializers.BooleanField()


class ListRequestSerializer(BaseRequestSerializer):
    """
    Base serializer for list/filter requests
    
    Provides common fields for filtering, sorting, and pagination.
    """
    page = serializers.IntegerField(default=1, min_value=1, required=False)
    page_size = serializers.IntegerField(default=20, min_value=1, max_value=100, required=False)
    search = serializers.CharField(required=False, allow_blank=True)
    ordering = serializers.CharField(required=False, allow_blank=True)
    
    def validate_ordering(self, value):
        """Validate ordering field"""
        if value and value.strip():
            # Remove leading - for descending order
            field = value.lstrip('-')
            allowed_fields = getattr(self.Meta, 'ordering_fields', [])
            if allowed_fields and field not in allowed_fields:
                raise serializers.ValidationError(
                    f"Invalid ordering field. Allowed: {', '.join(allowed_fields)}"
                )
        return value


class BulkOperationSerializer(BaseRequestSerializer):
    """Base serializer for bulk operations"""
    ids = serializers.ListField(
        child=serializers.CharField(),
        min_length=1,
        required=True,
        help_text="List of resource IDs"
    )


class IDListRequestSerializer(serializers.Serializer):
    """Serializer for requests with list of IDs"""
    ids = serializers.ListField(
        child=serializers.CharField(max_length=18),
        min_length=1,
        help_text="List of resource IDs (max 18 chars each)"
    )
