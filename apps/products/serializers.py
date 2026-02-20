"""
Product Performance API serializers.
"""
from rest_framework import serializers


class ProductPerformanceSerializer(serializers.Serializer):
    """Product performance data representation."""
    
    productId = serializers.CharField()
    productName = serializers.CharField()
    actualRevenue = serializers.DecimalField(max_digits=18, decimal_places=2)
    forecastRevenue = serializers.DecimalField(max_digits=18, decimal_places=2)
    deviation = serializers.DecimalField(max_digits=18, decimal_places=2)
    deviationPercent = serializers.DecimalField(max_digits=10, decimal_places=2)


class ProductPerformanceResponseSerializer(serializers.Serializer):
    """Product performance response wrapper."""
    
    topPerformers = ProductPerformanceSerializer(many=True)
    bottomPerformers = ProductPerformanceSerializer(many=True)
