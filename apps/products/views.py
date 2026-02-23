"""
Product Performance API views.
"""
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
)
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from core.api.responses import APIResponse, ErrorResponse

from .serializers import (
    ProductPerformanceResponseSerializer,
    QuarterlyPerformanceResponseSerializer,
)
from .services import ProductPerformanceService, get_quarterly_performance


class QuarterlyPerformanceAPIView(APIView):
    """
    GET /api/products/performance/achieved/

    Achieved by quarter or year: target vs actual + rebate for Q1–Q4 and Year.
    Pass account_id and year. Logic depends on frame agreement type:
    Quarterly, Quarterly & Volume, or Growth. Missing data returned as 0.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Products"],
        summary="Achieved (by quarter or year)",
        description=(
            "Returns Achieved (target vs actual, money + %) and Rebate for each quarter (Q1–Q4) and for the Year. "
            "Logic depends on frame agreement type: Quarterly, Quarterly & Volume, or Growth. "
            "Missing data returned as 0. Currency symbol from account's acc_currency_iso_code."
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
                name="year",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Calendar year (e.g., 2026).",
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=QuarterlyPerformanceResponseSerializer,
                description="Achieved and rebate per period (Q1–Q4 and Year).",
            ),
            422: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Validation error (e.g. missing account_id, invalid year).",
            ),
        },
    )
    def get(self, request):
        account_id = (request.query_params.get("account_id") or "").strip()
        year_param = request.query_params.get("year")

        if not account_id:
            return ErrorResponse.validation_error(
                message="Invalid query parameters",
                errors=[{"field": "account_id", "message": "account_id is required"}],
            )
        if year_param is None or year_param == "":
            return ErrorResponse.validation_error(
                message="Invalid query parameters",
                errors=[{"field": "year", "message": "year is required"}],
            )
        try:
            year = int(year_param)
        except (ValueError, TypeError):
            return ErrorResponse.validation_error(
                message="Invalid query parameters",
                errors=[{"field": "year", "message": "year must be an integer (e.g. 2026)"}],
            )
        if year < 2000 or year > 2100:
            return ErrorResponse.validation_error(
                message="Invalid query parameters",
                errors=[{"field": "year", "message": "year must be between 2000 and 2100"}],
            )

        data = get_quarterly_performance(account_id, year)
        return APIResponse.success(
            data=data,
            message="Achieved (by quarter or year) retrieved successfully",
        )


class ProductDeviationPerformanceAPIView(APIView):
    """
    GET /api/products/performance/deviation/

    Top 3 and bottom 3 products by deviation (forecast vs actual invoice revenue).
    Pass account_id, from, and to (YYYY-MM).
    """

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Products"],
        summary="Deviation (forecast vs actual by product)",
        description=(
            "Returns top 3 and bottom 3 products by deviation between "
            "approved forecast revenue and actual invoice revenue for the given account and date range. "
            "Pass account_id, from (YYYY-MM), and to (YYYY-MM)."
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
                description="Start month YYYY-MM (e.g., 2025-07).",
            ),
            OpenApiParameter(
                name="to",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="End month YYYY-MM (e.g., 2025-12).",
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=ProductPerformanceResponseSerializer,
                description="Top and bottom performers with deviation (£) and deviation percent.",
            ),
            422: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Validation error (e.g. missing params, invalid date range).",
            ),
        },
    )
    def get(self, request):
        account_id = (request.query_params.get("account_id") or "").strip()
        from_month = (request.query_params.get("from") or "").strip()
        to_month = (request.query_params.get("to") or "").strip()

        if not account_id:
            return ErrorResponse.validation_error(
                message="Invalid query parameters",
                errors=[{"field": "account_id", "message": "account_id is required"}],
            )
        if not from_month:
            return ErrorResponse.validation_error(
                message="Invalid query parameters",
                errors=[{"field": "from", "message": "from (YYYY-MM) is required"}],
            )
        if not to_month:
            return ErrorResponse.validation_error(
                message="Invalid query parameters",
                errors=[{"field": "to", "message": "to (YYYY-MM) is required"}],
            )

        try:
            from_date, to_date = ProductPerformanceService.parse_month_range(
                from_month, to_month
            )
            if from_date > to_date:
                return ErrorResponse.validation_error(
                    message="Invalid date range",
                    errors=[{"field": "to", "message": "End date must be >= start date"}],
                )
            performance_data = ProductPerformanceService.get_product_performance(
                from_date, to_date, account_id
            )
            return APIResponse.success(
                data=performance_data,
                message="Product performance data retrieved successfully",
            )
        except ValueError as e:
            return ErrorResponse.validation_error(
                message="Invalid date format",
                errors=[{"field": "from/to", "message": str(e)}],
            )
        except Exception as e:
            return ErrorResponse.server_error(
                message="An error occurred while retrieving product performance data",
                error_code="PERFORMANCE_CALCULATION_ERROR",
            )
