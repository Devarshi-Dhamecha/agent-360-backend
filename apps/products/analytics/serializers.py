"""
Analytics Serializers

Serializers for analytics API request validation and response formatting.
"""
from rest_framework import serializers


class AnalyticsQuerySerializer(serializers.Serializer):
    """Serializer for analytics query parameters"""
    
    level = serializers.ChoiceField(
        choices=['family', 'product', 'invoice'],
        required=True,
        help_text="Aggregation level: family, product, or invoice"
    )
    parent_id = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=False,
        help_text="Parent ID for drill-down (required for product and invoice levels)"
    )
    start_month = serializers.RegexField(
        regex=r'^\d{4}-\d{2}$',
        required=True,
        help_text="Start month in YYYY-MM format (e.g., 2025-03)"
    )
    end_month = serializers.RegexField(
        regex=r'^\d{4}-\d{2}$',
        required=True,
        help_text="End month in YYYY-MM format (e.g., 2025-10)"
    )
    top_n = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
        help_text="Limit results to top N records"
    )
    ordering = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=False,
        default='-actual_sales',
        help_text="Field to order by (prefix with - for descending, e.g., -actual_sales)"
    )
    
    def validate(self, attrs):
        """Validate that parent_id is provided for product and invoice levels"""
        level = attrs.get('level')
        parent_id = attrs.get('parent_id')
        
        if level in ['product', 'invoice'] and not parent_id:
            raise serializers.ValidationError({
                'parent_id': f'parent_id is required for level "{level}"'
            })
        
        return attrs


class AnalyticsResultSerializer(serializers.Serializer):
    """Serializer for individual analytics result"""
    
    id = serializers.CharField()
    name = serializers.CharField()
    status = serializers.CharField(allow_null=True)
    actual_sales = serializers.FloatField()
    rfc = serializers.FloatField()
    last_year_sales = serializers.FloatField()
    deviation_percent = serializers.FloatField()
    is_drillable = serializers.BooleanField()


class ChartDataSerializer(serializers.Serializer):
    """Serializer for chart data"""
    
    label = serializers.CharField()
    value = serializers.FloatField()


class AnalyticsResponseSerializer(serializers.Serializer):
    """Serializer for analytics response data"""
    
    level = serializers.CharField()
    start_month = serializers.CharField()
    end_month = serializers.CharField()
    total_actual_sales = serializers.FloatField()
    total_rfc = serializers.FloatField()
    total_last_year_sales = serializers.FloatField()
    chart_data = ChartDataSerializer(many=True)
    results = AnalyticsResultSerializer(many=True)
