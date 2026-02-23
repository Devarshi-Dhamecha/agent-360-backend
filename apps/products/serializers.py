"""
Product Performance API serializers.
"""
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer


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


# --- RFC by month (Draft + Approved + LY) ---


class RfcByMonthItemSerializer(serializers.Serializer):
    """One month: LY + draft + approved."""
    month = serializers.CharField()
    monthLabel = serializers.CharField()
    lyQty = serializers.FloatField()
    lyValue = serializers.FloatField()
    draftRfcQty = serializers.FloatField()
    draftRfcValue = serializers.FloatField()
    approvedRfcQty = serializers.FloatField()
    approvedRfcValue = serializers.FloatField()


class RfcByMonthProductSerializer(serializers.Serializer):
    """One product with months."""
    productId = serializers.CharField()
    productName = serializers.CharField()
    months = RfcByMonthItemSerializer(many=True)


@extend_schema_serializer(
    component_name="RfcByMonthResponse",
    description="RFC by month. Top-level data: accountId, from (start month YYYY-MM), to, currencySymbol, products. Each product has months[] with month, monthLabel, lyQty, lyValue, draftRfcQty, draftRfcValue, approvedRfcQty, approvedRfcValue. Note: actual JSON uses key 'from' for start month.",
)
class RfcByMonthResponseSerializer(serializers.Serializer):
    """RFC by month response wrapper. Actual response data uses key 'from' for start month."""
    accountId = serializers.CharField()
    from_ = serializers.CharField(source="from", required=False)
    to = serializers.CharField()
    currencySymbol = serializers.CharField(allow_null=True, required=False)
    products = RfcByMonthProductSerializer(many=True)
