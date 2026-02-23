"""
Product Performance API views.
"""
from drf_spectacular.utils import (
    OpenApiExample,
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
    RfcByMonthResponseSerializer,
)
from .services import ProductPerformanceService, get_quarterly_performance
from . import rfc_services


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


class RfcByMonthAPIView(APIView):
    """
    GET /api/products/rfc-by-month/

    Returns Draft and Approved RFC qty/value plus Last Year (LY) qty/value per product per month.
    Optional from/to; when omitted, range = current month through same month next year; LY = same window back one year.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Products"],
        summary="RFC by month (Draft + Approved + LY)",
        description=(
            "Returns both Draft and Approved RFC quantity/value and Last Year (LY) quantity/value "
            "per product per month. Pass account_id and product_ids (comma-separated). "
            "Optional from/to (YYYY-MM); if omitted, range = current month to same month next year, LY = that window − 1 year. "
            "Frontend switches Draft vs Approved using data keys (draftRfcQty/draftRfcValue vs approvedRfcQty/approvedRfcValue)."
        ),
        parameters=[
            OpenApiParameter(
                name="account_id",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Salesforce Account ID",
            ),
            OpenApiParameter(
                name="product_ids",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Comma-separated product Salesforce IDs (e.g. PRD-001,PRD-002)",
            ),
            OpenApiParameter(
                name="from",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Start month YYYY-MM (optional; default: current month)",
            ),
            OpenApiParameter(
                name="to",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description="End month YYYY-MM (optional; default: same month next year)",
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=RfcByMonthResponseSerializer,
                description=(
                    "RFC by month. Response data includes: accountId, from (start month YYYY-MM), to, currencySymbol, "
                    "products[].productId, productName, months[].month, monthLabel, lyQty, lyValue, "
                    "draftRfcQty, draftRfcValue, approvedRfcQty, approvedRfcValue."
                ),
                examples=[
                    OpenApiExample(
                        "Success",
                        value={
                            "success": True,
                            "message": "RFC by month retrieved successfully",
                            "data": {
                                "accountId": "0011234567890ABC",
                                "from": "2026-02",
                                "to": "2026-09",
                                "currencySymbol": "£",
                                "products": [
                                    {
                                        "productId": "PRD-001",
                                        "productName": "Roundup",
                                        "months": [
                                            {
                                                "month": "2026-02",
                                                "monthLabel": "February 2026",
                                                "lyQty": 0.0,
                                                "lyValue": 35000.0,
                                                "draftRfcQty": 250.0,
                                                "draftRfcValue": 225000.0,
                                                "approvedRfcQty": 240.0,
                                                "approvedRfcValue": 216000.0,
                                                "rejectionReason": None,
                                            },
                                        ],
                                    },
                                ],
                            },
                        },
                        response_only=True,
                        status_codes=["200"],
                    ),
                ],
            ),
            422: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Validation error (missing account_id/product_ids, invalid date range or format).",
                examples=[
                    OpenApiExample(
                        "Missing account_id",
                        value={
                            "success": False,
                            "message": "Invalid query parameters",
                            "errors": [
                                {"field": "account_id", "message": "account_id is required"}
                            ],
                        },
                        response_only=True,
                        status_codes=["422"],
                    ),
                    OpenApiExample(
                        "Missing product_ids",
                        value={
                            "success": False,
                            "message": "Invalid query parameters",
                            "errors": [
                                {"field": "product_ids", "message": "At least one product_id is required"}
                            ],
                        },
                        response_only=True,
                        status_codes=["422"],
                    ),
                ],
            ),
        },
    )
    def get(self, request):
        account_id = (request.query_params.get("account_id") or "").strip()
        product_ids_raw = (request.query_params.get("product_ids") or "").strip()
        from_month = (request.query_params.get("from") or "").strip()
        to_month = (request.query_params.get("to") or "").strip()

        if not account_id:
            return ErrorResponse.validation_error(
                message="Invalid query parameters",
                errors=[{"field": "account_id", "message": "account_id is required"}],
            )
        if not product_ids_raw:
            return ErrorResponse.validation_error(
                message="Invalid query parameters",
                errors=[{"field": "product_ids", "message": "At least one product_id is required"}],
            )

        product_ids = [p.strip() for p in product_ids_raw.split(",") if p.strip()]
        if not product_ids:
            return ErrorResponse.validation_error(
                message="Invalid query parameters",
                errors=[{"field": "product_ids", "message": "At least one product_id is required"}],
            )

        if from_month and to_month:
            try:
                from_date, to_date = rfc_services._parse_dates(from_month, to_month)
                if from_date > to_date:
                    return ErrorResponse.validation_error(
                        message="Invalid date range",
                        errors=[{"field": "to", "message": "End month must be on or after start month"}],
                    )
            except (ValueError, IndexError) as e:
                return ErrorResponse.validation_error(
                    message="Invalid date format",
                    errors=[{"field": "from/to", "message": "Must be YYYY-MM"}],
                )
        else:
            from_date, to_date = rfc_services._default_month_range()

        data = rfc_services.get_rfc_by_month(
            account_id=account_id,
            product_ids=product_ids,
            from_date=from_date,
            to_date=to_date,
        )
        return APIResponse.success(
            data=data,
            message="RFC by month retrieved successfully",
        )
