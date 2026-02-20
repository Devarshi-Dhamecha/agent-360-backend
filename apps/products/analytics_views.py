"""
Sales Analytics API views.
"""
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from django.core.paginator import Paginator, EmptyPage

from core.api.responses import APIResponse, ErrorResponse

from .analytics_serializers import (
    ProductFamilySerializer,
    ProductAnalyticsSerializer,
    OrderContributionSerializer,
    OrderDetailsSerializer,
)
from .analytics_services import SalesAnalyticsService


class ProductFamilyAnalyticsAPIView(APIView):
    """
    GET /api/sales/family - Get product family level sales analytics.
    
    Query parameters:
    - accountId (required): Salesforce Account ID
    - from (required): Start month in YYYY-MM format
    - to (required): End month in YYYY-MM format
    - page (optional): Page number (default: 1)
    - page_size (optional): Items per page (default: 20, max: 100)
    
    Returns product family analytics with actuals, last year, and RFC.
    """
    
    permission_classes = [AllowAny]
    
    @extend_schema(
        tags=["Sales Analytics"],
        summary="Get product family sales analytics",
        description=(
            "Returns product family level sales analytics including actual sales, "
            "open sales, last year sales, RFC (forecast), and deviation percentage.\n\n"
            "**Calculation Logic:**\n"
            "- Actual Sales: SUM(order_line_items.ori_ordered_amount)\n"
            "- Open Sales: SUM(order_line_items.ori_open_amount)\n"
            "- Last Year Sales: Same calculation for previous year date range\n"
            "- RFC: SUM(forecast.arf_approved_value) for approved forecasts\n"
            "- Deviation %: ((actualSales - rfc) / rfc) * 100"
        ),
        parameters=[
            OpenApiParameter(
                name="accountId",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Salesforce Account ID",
            ),
            OpenApiParameter(
                name="from",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Start month in YYYY-MM format (e.g., 2025-01)",
            ),
            OpenApiParameter(
                name="to",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="End month in YYYY-MM format (e.g., 2025-12)",
            ),
            OpenApiParameter(
                name="page",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Page number (default: 1)",
            ),
            OpenApiParameter(
                name="page_size",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Items per page (default: 20, max: 100)",
            ),
        ],
        responses={200: ProductFamilySerializer(many=True)},
    )
    def get(self, request):
        account_id = (request.query_params.get("accountId") or "").strip()
        from_month = (request.query_params.get("from") or "").strip()
        to_month = (request.query_params.get("to") or "").strip()
        
        # Pagination parameters
        try:
            page = int(request.query_params.get("page", 1))
            page_size = min(int(request.query_params.get("page_size", 20)), 100)
        except ValueError:
            return ErrorResponse.validation_error(
                message="Invalid pagination parameters",
                errors=[{"field": "page/page_size", "message": "Must be valid integers"}]
            )
        
        errors = []
        
        if not account_id:
            errors.append({
                "field": "accountId",
                "message": "accountId parameter is required"
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
            from_date, to_date = SalesAnalyticsService.parse_month_range(
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
            
            # Get analytics data
            analytics_data = SalesAnalyticsService.get_product_family_analytics(
                account_id, from_date, to_date
            )
            
            # Paginate results
            paginator = Paginator(analytics_data, page_size)
            try:
                paginated_data = paginator.page(page)
            except EmptyPage:
                paginated_data = paginator.page(paginator.num_pages) if paginator.num_pages > 0 else []
            
            return APIResponse.paginated(
                data=list(paginated_data) if hasattr(paginated_data, '__iter__') else [],
                page=page,
                page_size=page_size,
                total_count=paginator.count,
                message="Product family analytics retrieved successfully"
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
                message="An error occurred while retrieving analytics data",
                error_code="ANALYTICS_CALCULATION_ERROR"
            )


class ProductAnalyticsAPIView(APIView):
    """
    GET /api/sales/product - Get product level sales analytics.
    
    Query parameters:
    - accountId (required): Salesforce Account ID
    - family (required): Product family name
    - from (required): Start month in YYYY-MM format
    - to (required): End month in YYYY-MM format
    - page (optional): Page number (default: 1)
    - page_size (optional): Items per page (default: 20, max: 100)
    
    Returns product analytics for a specific family.
    """
    
    permission_classes = [AllowAny]
    
    @extend_schema(
        tags=["Sales Analytics"],
        summary="Get product sales analytics by family",
        description=(
            "Returns product level sales analytics for a specific product family.\n\n"
            "**Calculation Logic:**\n"
            "- Actual Sales: SUM(order_line_items.ori_ordered_amount) per product\n"
            "- Open Sales: SUM(order_line_items.ori_open_amount) per product\n"
            "- Last Year Sales: Same calculation for previous year date range\n"
            "- RFC: SUM(forecast.arf_approved_value) per product\n"
            "- Deviation %: ((actualSales - rfc) / rfc) * 100"
        ),
        parameters=[
            OpenApiParameter(
                name="accountId",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Salesforce Account ID",
            ),
            OpenApiParameter(
                name="family",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Product family name",
            ),
            OpenApiParameter(
                name="from",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Start month in YYYY-MM format (e.g., 2025-01)",
            ),
            OpenApiParameter(
                name="to",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="End month in YYYY-MM format (e.g., 2025-12)",
            ),
            OpenApiParameter(
                name="page",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Page number (default: 1)",
            ),
            OpenApiParameter(
                name="page_size",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Items per page (default: 20, max: 100)",
            ),
        ],
        responses={200: ProductAnalyticsSerializer(many=True)},
    )
    def get(self, request):
        account_id = (request.query_params.get("accountId") or "").strip()
        family = (request.query_params.get("family") or "").strip()
        from_month = (request.query_params.get("from") or "").strip()
        to_month = (request.query_params.get("to") or "").strip()
        
        # Pagination parameters
        try:
            page = int(request.query_params.get("page", 1))
            page_size = min(int(request.query_params.get("page_size", 20)), 100)
        except ValueError:
            return ErrorResponse.validation_error(
                message="Invalid pagination parameters",
                errors=[{"field": "page/page_size", "message": "Must be valid integers"}]
            )
        
        errors = []
        
        if not account_id:
            errors.append({
                "field": "accountId",
                "message": "accountId parameter is required"
            })
        
        if not family:
            errors.append({
                "field": "family",
                "message": "family parameter is required"
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
            from_date, to_date = SalesAnalyticsService.parse_month_range(
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
            
            # Get analytics data
            analytics_data = SalesAnalyticsService.get_product_analytics(
                account_id, family, from_date, to_date
            )
            
            # Paginate results
            paginator = Paginator(analytics_data, page_size)
            try:
                paginated_data = paginator.page(page)
            except EmptyPage:
                paginated_data = paginator.page(paginator.num_pages) if paginator.num_pages > 0 else []
            
            return APIResponse.paginated(
                data=list(paginated_data) if hasattr(paginated_data, '__iter__') else [],
                page=page,
                page_size=page_size,
                total_count=paginator.count,
                message="Product analytics retrieved successfully"
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
                message="An error occurred while retrieving analytics data",
                error_code="ANALYTICS_CALCULATION_ERROR"
            )


class OrderContributionAPIView(APIView):
    """
    GET /api/sales/orders - Get order contribution for a product.
    
    Query parameters:
    - accountId (required): Salesforce Account ID
    - productId (required): Product Salesforce ID
    - from (required): Start month in YYYY-MM format
    - to (required): End month in YYYY-MM format
    - page (optional): Page number (default: 1)
    - page_size (optional): Items per page (default: 20, max: 100)
    
    Returns order contribution showing selected product's contribution per order.
    """
    
    permission_classes = [AllowAny]
    
    @extend_schema(
        tags=["Sales Analytics"],
        summary="Get order contribution by product",
        description=(
            "Returns order contribution showing how much a specific product "
            "contributed to each order.\n\n"
            "**Shows only the selected product's contribution per order.**"
        ),
        parameters=[
            OpenApiParameter(
                name="accountId",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Salesforce Account ID",
            ),
            OpenApiParameter(
                name="productId",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Product Salesforce ID",
            ),
            OpenApiParameter(
                name="from",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Start month in YYYY-MM format (e.g., 2025-01)",
            ),
            OpenApiParameter(
                name="to",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="End month in YYYY-MM format (e.g., 2025-12)",
            ),
            OpenApiParameter(
                name="page",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Page number (default: 1)",
            ),
            OpenApiParameter(
                name="page_size",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Items per page (default: 20, max: 100)",
            ),
        ],
        responses={200: OrderContributionSerializer(many=True)},
    )
    def get(self, request):
        account_id = (request.query_params.get("accountId") or "").strip()
        product_id = (request.query_params.get("productId") or "").strip()
        from_month = (request.query_params.get("from") or "").strip()
        to_month = (request.query_params.get("to") or "").strip()
        
        # Pagination parameters
        try:
            page = int(request.query_params.get("page", 1))
            page_size = min(int(request.query_params.get("page_size", 20)), 100)
        except ValueError:
            return ErrorResponse.validation_error(
                message="Invalid pagination parameters",
                errors=[{"field": "page/page_size", "message": "Must be valid integers"}]
            )
        
        errors = []
        
        if not account_id:
            errors.append({
                "field": "accountId",
                "message": "accountId parameter is required"
            })
        
        if not product_id:
            errors.append({
                "field": "productId",
                "message": "productId parameter is required"
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
            from_date, to_date = SalesAnalyticsService.parse_month_range(
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
            
            # Get order contribution data
            contribution_data = SalesAnalyticsService.get_order_contribution(
                account_id, product_id, from_date, to_date
            )
            
            # Paginate results
            paginator = Paginator(contribution_data, page_size)
            try:
                paginated_data = paginator.page(page)
            except EmptyPage:
                paginated_data = paginator.page(paginator.num_pages) if paginator.num_pages > 0 else []
            
            return APIResponse.paginated(
                data=list(paginated_data) if hasattr(paginated_data, '__iter__') else [],
                page=page,
                page_size=page_size,
                total_count=paginator.count,
                message="Order contribution data retrieved successfully"
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
                message="An error occurred while retrieving order contribution data",
                error_code="ANALYTICS_CALCULATION_ERROR"
            )


class OrderDetailsAPIView(APIView):
    """
    GET /api/sales/order-details - Get all product details for an order.
    
    Query parameters:
    - accountId (required): Salesforce Account ID
    - orderId (required): Order Salesforce ID
    - from (required): Start month in YYYY-MM format
    - to (required): End month in YYYY-MM format
    - page (optional): Page number (default: 1)
    - page_size (optional): Items per page (default: 20, max: 100)
    
    Returns all products inside the order with their details.
    """
    
    permission_classes = [AllowAny]
    
    @extend_schema(
        tags=["Sales Analytics"],
        summary="Get order details with all products",
        description=(
            "Returns all products inside a specific order with their quantities and amounts.\n\n"
            "**Shows ALL products in the order, not just one.**"
        ),
        parameters=[
            OpenApiParameter(
                name="accountId",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Salesforce Account ID",
            ),
            OpenApiParameter(
                name="orderId",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Order Salesforce ID",
            ),
            OpenApiParameter(
                name="from",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Start month in YYYY-MM format (e.g., 2025-01)",
            ),
            OpenApiParameter(
                name="to",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="End month in YYYY-MM format (e.g., 2025-12)",
            ),
            OpenApiParameter(
                name="page",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Page number (default: 1)",
            ),
            OpenApiParameter(
                name="page_size",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Items per page (default: 20, max: 100)",
            ),
        ],
        responses={200: OrderDetailsSerializer(many=True)},
    )
    def get(self, request):
        account_id = (request.query_params.get("accountId") or "").strip()
        order_id = (request.query_params.get("orderId") or "").strip()
        from_month = (request.query_params.get("from") or "").strip()
        to_month = (request.query_params.get("to") or "").strip()
        
        # Pagination parameters
        try:
            page = int(request.query_params.get("page", 1))
            page_size = min(int(request.query_params.get("page_size", 20)), 100)
        except ValueError:
            return ErrorResponse.validation_error(
                message="Invalid pagination parameters",
                errors=[{"field": "page/page_size", "message": "Must be valid integers"}]
            )
        
        errors = []
        
        if not account_id:
            errors.append({
                "field": "accountId",
                "message": "accountId parameter is required"
            })
        
        if not order_id:
            errors.append({
                "field": "orderId",
                "message": "orderId parameter is required"
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
            from_date, to_date = SalesAnalyticsService.parse_month_range(
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
            
            # Get order details data
            details_data = SalesAnalyticsService.get_order_details(
                account_id, order_id, from_date, to_date
            )
            
            # Paginate results
            paginator = Paginator(details_data, page_size)
            try:
                paginated_data = paginator.page(page)
            except EmptyPage:
                paginated_data = paginator.page(paginator.num_pages) if paginator.num_pages > 0 else []
            
            return APIResponse.paginated(
                data=list(paginated_data) if hasattr(paginated_data, '__iter__') else [],
                page=page,
                page_size=page_size,
                total_count=paginator.count,
                message="Order details retrieved successfully"
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
                message="An error occurred while retrieving order details",
                error_code="ANALYTICS_CALCULATION_ERROR"
            )
