"""
User API serializers.
"""
from rest_framework import serializers

from .models import User


class UserListSerializer(serializers.ModelSerializer):
    """User in list responses."""
    id = serializers.CharField(source='usr_sf_id', read_only=True)
    full_name = serializers.CharField(source='usr_name', read_only=True)
    email = serializers.EmailField(source='usr_email', read_only=True)
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'role']

    def get_role(self, obj):
        """Return role name if user has a role assigned."""
        if obj.usr_user_role_id:
            return obj.usr_user_role_id.ur_name
        return None
