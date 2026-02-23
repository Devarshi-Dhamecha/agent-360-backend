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


# --- Quarterly / Year performance (Achieved + Rebate) ---


class QuarterlyAchievedSerializer(serializers.Serializer):
    """Achieved block for a period."""
    target = serializers.FloatField()
    actual = serializers.FloatField()
    difference = serializers.FloatField()
    percent = serializers.FloatField()
    label = serializers.CharField()


class QuarterlyPeriodSerializer(serializers.Serializer):
    """One period (Q1, Q2, Q3, Q4, Year) with achieved and rebate."""
    period = serializers.CharField()
    achieved = QuarterlyAchievedSerializer()
    rebate = serializers.FloatField()
    rebate_label = serializers.CharField()


class QuarterlyPerformanceResponseSerializer(serializers.Serializer):
    """Quarterly/year performance response wrapper."""
    accountId = serializers.CharField()
    year = serializers.IntegerField()
    currencySymbol = serializers.CharField(allow_null=True, required=False)
    agreementType = serializers.CharField(allow_null=True)
    periods = serializers.DictField(
        child=QuarterlyPeriodSerializer(),
        allow_empty=True,
    )
