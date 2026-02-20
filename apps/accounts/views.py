"""
Account API views.
"""
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from core.api.responses import APIResponse, ErrorResponse
from core.api.utils.pagination import StandardPagination

from .models import Account
from .serializers import AccountListSerializer


@extend_schema(
    parameters=[
        OpenApiParameter(
            name='page',
            type=int,
            location=OpenApiParameter.QUERY,
            description='Page number (if provided, enables pagination)',
            required=False,
        ),
        OpenApiParameter(
            name='page_size',
            type=int,
            location=OpenApiParameter.QUERY,
            description='Page size (max 100, if provided, enables pagination)',
            required=False,
        ),
    ],
)
class AccountListAPIView(APIView):
    """GET /api/accounts/ - list all accounts (paginated if page/page_size provided)."""
    permission_classes = [AllowAny]

    def get(self, request):
        qs = Account.objects.select_related('acc_owner_id').all()
        qs = qs.order_by('acc_name')

        # Check if pagination parameters are provided
        page_param = request.query_params.get('page')
        page_size_param = request.query_params.get('page_size')

        # If either pagination parameter is provided, use pagination
        if page_param is not None or page_size_param is not None:
            paginator = StandardPagination()
            page = paginator.paginate_queryset(qs, request)
            serializer = AccountListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        # Otherwise, return all data without pagination
        serializer = AccountListSerializer(qs, many=True)
        return APIResponse.success(
            data=serializer.data,
            message='Data retrieved successfully'
        )


@extend_schema(
    parameters=[
        OpenApiParameter(
            name='page',
            type=int,
            location=OpenApiParameter.QUERY,
            description='Page number (if provided, enables pagination)',
            required=False,
        ),
        OpenApiParameter(
            name='page_size',
            type=int,
            location=OpenApiParameter.QUERY,
            description='Page size (max 100, if provided, enables pagination)',
            required=False,
        ),
    ],
)
class AccountsByUserAPIView(APIView):
    """GET /api/accounts/user/{user_id}/ - list accounts by user (paginated if page/page_size provided)."""
    permission_classes = [AllowAny]

    def get(self, request, user_id):
        # Validate user_id is provided
        if not user_id or not user_id.strip():
            return ErrorResponse.bad_request(
                message="User ID is required",
                errors=[{"field": "user_id", "message": "User ID cannot be empty"}],
                error_code="REQUIRED_FIELD_MISSING"
            )

        user_id = user_id.strip()

        qs = Account.objects.select_related('acc_owner_id').filter(acc_owner_id_id=user_id)
        qs = qs.order_by('acc_name')

        # Check if pagination parameters are provided
        page_param = request.query_params.get('page')
        page_size_param = request.query_params.get('page_size')

        # If either pagination parameter is provided, use pagination
        if page_param is not None or page_size_param is not None:
            paginator = StandardPagination()
            page = paginator.paginate_queryset(qs, request)
            serializer = AccountListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        # Otherwise, return all data without pagination
        serializer = AccountListSerializer(qs, many=True)
        return APIResponse.success(
            data=serializer.data,
            message='Data retrieved successfully'
        )
