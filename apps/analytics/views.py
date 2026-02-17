"""
Analytics Views

API views for analytics endpoints.
"""
from rest_framework.views import APIView
from rest_framework import status

from core.api.responses.base import APIResponse
from .serializers import AnalyticsQuerySerializer
from .services import AnalyticsService


class AnalyticsAPIView(APIView):
    """
    Analytics API endpoint for hierarchical data aggregation.
    
    GET /api/analytics/
    
    Query Parameters:
        - level (required): Aggregation level (family, product, invoice)
        - parent_id (conditional): Parent ID for drill-down (required for product and invoice)
        - start_month (required): Start month in YYYY-MM format
        - end_month (required): End month in YYYY-MM format
        - top_n (optional): Limit results to top N records
        - ordering (optional): Field to order by (default: -actual_sales)
    
    Returns:
        Hierarchical analytics data with actual sales, RFC, and last year sales
    """
    
    def get(self, request):
        """
        Handle GET request for analytics data.
        
        Args:
            request: HTTP request object
            
        Returns:
            Response with analytics data or error
        """
        # Validate query parameters
        serializer = AnalyticsQuerySerializer(data=request.query_params)
        
        if not serializer.is_valid():
            return APIResponse.error(
                message="Invalid query parameters",
                errors=[{"field": k, "message": v[0]} for k, v in serializer.errors.items()],
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        validated_data = serializer.validated_data
        
        # Initialize service
        service = AnalyticsService(
            level=validated_data['level'],
            start_month=validated_data['start_month'],
            end_month=validated_data['end_month'],
            parent_id=validated_data.get('parent_id'),
            top_n=validated_data.get('top_n'),
            ordering=validated_data.get('ordering', '-actual_sales')
        )
        
        # Validate service parameters
        is_valid, error_message = service.validate()
        if not is_valid:
            return APIResponse.error(
                message=error_message,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Get analytics data
        try:
            analytics_data = service.get_analytics()
            
            return APIResponse.success(
                data=analytics_data,
                message="Analytics fetched successfully",
                status_code=status.HTTP_200_OK
            )
        
        except Exception as e:
            return APIResponse.error(
                message="Failed to fetch analytics data",
                errors=[{"message": str(e)}],
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
