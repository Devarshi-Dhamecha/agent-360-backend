"""
Account API serializers.
"""
from rest_framework import serializers

from .models import Account


class AccountListSerializer(serializers.ModelSerializer):
    """Account in list responses."""
    id = serializers.CharField(source='acc_sf_id', read_only=True)
    name = serializers.CharField(source='acc_name', read_only=True)
    owner_id = serializers.SerializerMethodField()
    account_number = serializers.CharField(source='acc_account_number', read_only=True)
    currency_iso_code = serializers.CharField(source='acc_currency_iso_code', read_only=True)
    credit_limit = serializers.DecimalField(
        source='acc_credit_limit', max_digits=18, decimal_places=2, read_only=True
    )
    active = serializers.IntegerField(source='acc_active', read_only=True)

    class Meta:
        model = Account
        fields = [
            'id', 'name', 'owner_id', 'account_number',
            'currency_iso_code', 'credit_limit', 'active',
        ]

    def get_owner_id(self, obj):
        return obj.acc_owner_id_id if obj.acc_owner_id_id else None
