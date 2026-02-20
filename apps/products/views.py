"""
Product Performance API views.
"""
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from core.api.responses import APIResponse, ErrorResponse

from .serializers import ProductPerformanceResponseSerializer
from .services import ProductPerformanceService


class ProductPerformanceAPIView(APIView):
    """
    GET /api/products/performance - Get top and bottom performing products.
    
    Query parameters:
    - account_id (required): Salesforce Account ID
    - from (required): Start month in YYYY-MM format
    - to (required): End month in YYYY-MM format
    
    Returns top 3 and bottom 3 performing products based on deviation
    between approved forecast value and actual invoice revenue for the specified account.
    """
    
    permission_classes = [AllowAny]
    
    @extend_schema(
        tags=["Products"],
        summary="Get product performance variance by account",
        description=(
            "Returns top 3 and bottom 3 performing products based on deviation "
            "between approved forecast revenue and actual invoice revenue for a given account and date range.\n\n"
            "**Calculation Logic:**\n"
            "- Actual Revenue: SUM(invoice_line_items.net_price) for closed, valid invoices filtered by account\n"
            "- Forecast Revenue: SUM(forecast.arf_approved_value) for approved forecasts filtered by account\n"
            "- Deviation: actualRevenue - forecastRevenue\n"
            "- Deviation %: (deviation / forecastRevenue) * 100\n\n"
            "**Top Performers:** Products with highest positive deviation\n"
            "**Bottom Performers:** Products with lowest (most negative) deviation"
        ),
        parameters=[
            OpenApiParameter(
                name="account_id",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Salesforce Account ID (e.g., 0011234567890ABC)",
            ),
            OpenApiParameter(
                name="from",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Start month in YYYY-MM format (e.g., 2025-07)",
            ),
            OpenApiParameter(
                name="to",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="End month in YYYY-MM format (e.g., 2025-12)",
            ),
        ],
        responses={200: ProductPerformanceResponseSerializer},
    )
    def get(self, request):
        account_id = (request.query_params.get("account_id") or "").strip()
        from_month = (request.query_params.get("from") or "").strip()
        to_month = (request.query_params.get("to") or "").strip()
        
        errors = []
        
        if not account_id:
            errors.append({
                "field": "account_id",
                "message": "account_id parameter is required"
            })
        
        if not from_month:
            errors.append({
                "field": "from",
                "message": "from parameter is required in YYYY-MM format"
            })
        
        if not to_month:
            errors.append({
                "field": "to",
                "message": "to parameter is required in YYYY-MM format"
            })
        
        if errors:
            return ErrorResponse.validation_error(
                message="Invalid query parameters",
                errors=errors
            )
        
        try:
            # Parse and validate date range
            from_date, to_date = ProductPerformanceService.parse_month_range(
                from_month, to_month
            )
            
            # Validate date range
            if from_date > to_date:
                return ErrorResponse.validation_error(
                    message="Invalid date range",
                    errors=[{
                        "field": "to",
                        "message": "End date must be greater than or equal to start date"
                    }]
                )
            
            # Get performance data
            performance_data = ProductPerformanceService.get_product_performance(
                from_date, to_date, account_id
            )
            
            return APIResponse.success(
                data=performance_data,
                message="Product performance data retrieved successfully"
            )
            
        except ValueError as e:
            return ErrorResponse.validation_error(
                message="Invalid date format",
                errors=[{
                    "field": "from/to",
                    "message": str(e)
                }]
            )
        except Exception as e:
            return ErrorResponse.server_error(
                message="An error occurred while retrieving product performance data",
                error_code="PERFORMANCE_CALCULATION_ERROR"
            )
