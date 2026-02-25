"""
Complaints & Cases API views.
"""
from datetime import datetime
from django.db.models import Count, Q
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework import status

from core.api.responses import APIResponse
from core.api.utils.pagination import StandardPagination
from core.api.constants import (
    ErrorMessages, SuccessMessages, ErrorCodes, FieldNames, ValidationConstants
)

from .models import Case, CaseComment, CaseHistory
from .serializers import (
    CaseSummarySerializer,
    CaseListSerializer,
    CaseDetailSerializer,
    CaseCommentSerializer,
    CaseTimelineSerializer,
    CreateCaseCommentSerializer,
    CaseCommentResponseSerializer,
)

# Query param validation
STATUS_CHOICES = ValidationConstants.STATUS_CHOICES
ORDERING_MAP = {
    'opened_at': 'cs_sf_created_date',
    '-opened_at': '-cs_sf_created_date',
    'last_modified': 'cs_last_modified_date',
    '-last_modified': '-cs_last_modified_date',
}


def _parse_date(value, param_name):
    """Parse YYYY-MM-DD string; raise ValidationError if invalid."""
    if not value:
        return None
    try:
        return datetime.strptime(value.strip(), ValidationConstants.DATE_FORMAT).date()
    except ValueError:
        raise ValidationError({param_name: [ErrorMessages.DATE_FORMAT_INVALID]})

def _cases_queryset_with_counts():
    """Base Case queryset with comments_count and timeline_count annotations."""
    return Case.objects.annotate(
        # Use the reverse *query* names for relations (casecomment, casehistory)
        comments_count=Count('casecomment', distinct=True),
        timeline_count=Count('casehistory', distinct=True),
    )


@extend_schema(
    parameters=[
        OpenApiParameter(
            name='account_id',
            type=str,
            location=OpenApiParameter.QUERY,
            description='Filter summary by account Salesforce ID',
            required=True,
        ),
        OpenApiParameter(
            name='opened_from',
            type=str,
            location=OpenApiParameter.QUERY,
            description='Opened date from (YYYY-MM-DD)',
            required=False,
        ),
        OpenApiParameter(
            name='opened_to',
            type=str,
            location=OpenApiParameter.QUERY,
            description='Opened date to (YYYY-MM-DD)',
            required=False,
        ),
    ],
)
class CaseSummaryAPIView(APIView):
    """GET /api/complaints-cases/summary - open_count, total_count, closed_count with optional date filters."""
    permission_classes = [AllowAny]

    def get(self, request):
        account_id = (request.query_params.get('account_id') or '').strip()
        if not account_id:
            raise ValidationError({'account_id': [ErrorMessages.QUERY_PARAM_REQUIRED]})

        opened_from = request.query_params.get('opened_from') or ''
        opened_to = request.query_params.get('opened_to') or ''

        opened_from_d = _parse_date(opened_from, 'opened_from')
        opened_to_d = _parse_date(opened_to, 'opened_to')

        qs = Case.objects.all()
        qs = qs.filter(cs_account_id_id=account_id)

        # Apply date filters if provided
        if opened_from_d:
            qs = qs.filter(cs_sf_created_date__date__gte=opened_from_d)
        if opened_to_d:
            qs = qs.filter(cs_sf_created_date__date__lte=opened_to_d)

        total_count = qs.count()
        closed_count = qs.filter(cs_status__iexact='Closed').count()
        open_count = total_count - closed_count

        data = {
            'open_count': open_count,
            'total_count': total_count,
            'closed_count': closed_count,
        }
        serializer = CaseSummarySerializer(data)
        return APIResponse.success(
            data=serializer.data,
            message=SuccessMessages.SUMMARY_RETRIEVED,
        )


@extend_schema(
    parameters=[
        OpenApiParameter(
            name='status',
            type=str,
            location=OpenApiParameter.QUERY,
            description='Filter by status: open, closed, or all',
            required=False,
            enum=['open', 'closed', 'all'],
        ),
        OpenApiParameter(
            name='search',
            type=str,
            location=OpenApiParameter.QUERY,
            description='Search in subject and case number',
            required=False,
        ),
        OpenApiParameter(
            name='account_id',
            type=str,
            location=OpenApiParameter.QUERY,
            description='Filter by account Salesforce ID',
            required=False,
        ),
        OpenApiParameter(
            name='opened_from',
            type=str,
            location=OpenApiParameter.QUERY,
            description='Opened date from (YYYY-MM-DD)',
            required=False,
        ),
        OpenApiParameter(
            name='opened_to',
            type=str,
            location=OpenApiParameter.QUERY,
            description='Opened date to (YYYY-MM-DD)',
            required=False,
        ),
        OpenApiParameter(
            name='ordering',
            type=str,
            location=OpenApiParameter.QUERY,
            description='Sort order',
            required=False,
            enum=['opened_at', '-opened_at', 'last_modified', '-last_modified'],
        ),
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
class CaseListAPIView(APIView):
    """GET /api/complaints-cases - list with filters, ordering, optional pagination."""
    permission_classes = [AllowAny]

    def get(self, request):
        params = request.query_params
        status_filter = (params.get('status') or 'all').strip().lower()
        search = (params.get('search') or '').strip()
        account_id = (params.get('account_id') or '').strip()
        opened_from = params.get('opened_from') or ''
        opened_to = params.get('opened_to') or ''
        ordering_param = (params.get('ordering') or '-opened_at').strip()

        if status_filter not in STATUS_CHOICES:
            raise ValidationError({
                'status': [ErrorMessages.INVALID_STATUS.format(allowed=", ".join(STATUS_CHOICES))],
            })
        order_field = ORDERING_MAP.get(ordering_param)
        if not order_field:
            raise ValidationError({
                'ordering': [
                    ErrorMessages.INVALID_ORDERING.format(
                        allowed='opened_at, -opened_at, last_modified, -last_modified'
                    )
                ],
            })

        opened_from_d = _parse_date(opened_from, 'opened_from')
        opened_to_d = _parse_date(opened_to, 'opened_to')

        qs = _cases_queryset_with_counts()

        if status_filter == 'open':
            qs = qs.exclude(cs_status__iexact='Closed')
        elif status_filter == 'closed':
            qs = qs.filter(cs_status__iexact='Closed')

        if search:
            qs = qs.filter(
                Q(cs_subject__icontains=search) | Q(cs_case_number__icontains=search),
            )
        if account_id:
            qs = qs.filter(cs_account_id_id=account_id)
        if opened_from_d:
            qs = qs.filter(cs_sf_created_date__date__gte=opened_from_d)
        if opened_to_d:
            qs = qs.filter(cs_sf_created_date__date__lte=opened_to_d)

        qs = qs.order_by(order_field)

        # Check if pagination parameters are provided
        page_param = request.query_params.get('page')
        page_size_param = request.query_params.get('page_size')

        # If either pagination parameter is provided, use pagination
        if page_param is not None or page_size_param is not None:
            paginator = StandardPagination()
            page = paginator.paginate_queryset(qs, request)
            serializer = CaseListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        # Otherwise, return all data without pagination
        serializer = CaseListSerializer(qs, many=True)
        return APIResponse.success(
            data=serializer.data,
            message=SuccessMessages.DATA_RETRIEVED
        )


class CaseDetailAPIView(APIView):
    """GET /api/complaints-cases/{case_id} - single case with counts."""
    permission_classes = [AllowAny]

    def get(self, request, case_id):
        qs = _cases_queryset_with_counts()
        try:
            case = qs.get(cs_sf_id=case_id)
        except Case.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound(ErrorMessages.CASE_NOT_FOUND)
        serializer = CaseDetailSerializer(case)
        return APIResponse.success(
            data=serializer.data,
            message=SuccessMessages.CASE_RETRIEVED,
        )


@extend_schema(
    methods=['GET'],
    parameters=[
        OpenApiParameter(
            name='case_id',
            type=str,
            location=OpenApiParameter.PATH,
            description='Case Salesforce ID',
            required=True,
        ),
    ],
)
@extend_schema(
    methods=['POST'],
    request=CreateCaseCommentSerializer,
    responses={
        201: CaseCommentResponseSerializer,
        400: {'description': 'Validation error'},
        404: {'description': 'Case not found'},
    },
)
class CaseCommentsAPIView(APIView):
    """
    GET /api/complaints-cases/{case_id}/comments - comments latest first.
    POST /api/complaints-cases/{case_id}/comments - create new comment.
    """
    permission_classes = [AllowAny]

    def get(self, request, case_id):
        try:
            Case.objects.get(cs_sf_id=case_id)
        except Case.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound(ErrorMessages.CASE_NOT_FOUND)

        comments = (
            CaseComment.objects.filter(cc_case_id_id=case_id)
            .select_related('cc_agent_created_by', 'cc_sf_created_by_id')
            .order_by('-cc_id')
        )
        serializer = CaseCommentSerializer(comments, many=True)
        return APIResponse.success(
            data=serializer.data,
            message=SuccessMessages.COMMENTS_RETRIEVED,
        )

    def post(self, request, case_id):
        """Create a new case comment."""
        # Validate case exists
        try:
            case = Case.objects.get(cs_sf_id=case_id)
        except Case.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound(ErrorMessages.CASE_NOT_FOUND)

        # Validate input
        input_serializer = CreateCaseCommentSerializer(data=request.data)
        if not input_serializer.is_valid():
            raise ValidationError(input_serializer.errors)

        validated_data = input_serializer.validated_data

        # Create comment (dates will be handled by model's save method)
        comment = CaseComment.objects.create(
            cc_case_id=case,
            cc_comment_body=validated_data['comment_body'],
            cc_is_published=validated_data.get('is_published', True),
            cc_agent_created_by_id=validated_data['created_by_id'],
            cc_agent_created_date=timezone.now(),
            cc_agent360_source=True,
            cc_sync_status=0,  # Pending sync to Salesforce
            cc_version=1,
            cc_retry_count=0,
            cc_active=1,
        )

        # Fetch the created comment with related user data
        comment = CaseComment.objects.select_related('cc_agent_created_by').get(cc_id=comment.cc_id)

        # Serialize response
        output_serializer = CaseCommentResponseSerializer(comment)
        return APIResponse.created(
            data=output_serializer.data,
            message=SuccessMessages.COMMENT_CREATED,
            resource_id=str(comment.cc_id),
        )


class CaseTimelineAPIView(APIView):
    """GET /api/complaints-cases/{case_id}/timeline - case history latest first."""
    permission_classes = [AllowAny]

    def get(self, request, case_id):
        try:
            Case.objects.get(cs_sf_id=case_id)
        except Case.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound(ErrorMessages.CASE_NOT_FOUND)

        events = (
            CaseHistory.objects.filter(ch_case_id_id=case_id)
            .select_related('ch_created_by_id')
            .order_by('-ch_created_date')
        )
        serializer = CaseTimelineSerializer(events, many=True)
        return APIResponse.success(
            data=serializer.data,
            message=SuccessMessages.TIMELINE_RETRIEVED,
        )
