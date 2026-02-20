"""
Sales Analytics Serializers.
"""
from rest_framework import serializers


class ProductFamilySerializer(serializers.Serializer):
    """Serializer for Product Family analytics."""
    family = serializers.CharField()
    actualSales = serializers.DecimalField(max_digits=18, decimal_places=2)
    openSales = serializers.DecimalField(max_digits=18, decimal_places=2)
    lastYearSales = serializers.DecimalField(max_digits=18, decimal_places=2)
    rfc = serializers.DecimalField(max_digits=18, decimal_places=2)
    deviationPercent = serializers.DecimalField(max_digits=10, decimal_places=2)


class ProductAnalyticsSerializer(serializers.Serializer):
    """Serializer for Product analytics."""
    productId = serializers.CharField()
    productName = serializers.CharField()
    actualSales = serializers.DecimalField(max_digits=18, decimal_places=2)
    openSales = serializers.DecimalField(max_digits=18, decimal_places=2)
    lastYearSales = serializers.DecimalField(max_digits=18, decimal_places=2)
    rfc = serializers.DecimalField(max_digits=18, decimal_places=2)
    deviationPercent = serializers.DecimalField(max_digits=10, decimal_places=2)


class OrderContributionSerializer(serializers.Serializer):
    """Serializer for Order contribution analytics."""
    orderId = serializers.CharField()
    orderNumber = serializers.CharField()
    orderStatus = serializers.CharField()
    orderedQuantity = serializers.DecimalField(max_digits=18, decimal_places=2)
    orderedAmount = serializers.DecimalField(max_digits=18, decimal_places=2)
    openQuantity = serializers.DecimalField(max_digits=18, decimal_places=2)
    openAmount = serializers.DecimalField(max_digits=18, decimal_places=2)


class OrderDetailsSerializer(serializers.Serializer):
    """Serializer for Order details analytics."""
    productId = serializers.CharField()
    productName = serializers.CharField()
    status = serializers.CharField()
    orderedQuantity = serializers.DecimalField(max_digits=18, decimal_places=2)
    orderedAmount = serializers.DecimalField(max_digits=18, decimal_places=2)
    openQuantity = serializers.DecimalField(max_digits=18, decimal_places=2)
    openAmount = serializers.DecimalField(max_digits=18, decimal_places=2)
