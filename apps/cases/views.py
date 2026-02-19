"""
Complaints & Cases API views.
"""
from datetime import datetime
from django.db.models import Count, Q
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

from core.api.responses import APIResponse
from core.api.utils.pagination import StandardPagination

from .models import Case, CaseComment, CaseHistory
from .serializers import (
    CaseSummarySerializer,
    CaseListSerializer,
    CaseDetailSerializer,
    CaseCommentSerializer,
    CaseTimelineSerializer,
)

# Query param validation
STATUS_CHOICES = ('open', 'closed', 'all')
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
        return datetime.strptime(value.strip(), '%Y-%m-%d').date()
    except ValueError:
        raise ValidationError({param_name: ['Invalid date. Use YYYY-MM-DD.']})


def _cases_queryset_with_counts():
    """Base Case queryset with comments_count and timeline_count annotations."""
    return Case.objects.annotate(
        # Use the reverse *query* names for relations (casecomment, casehistory)
        comments_count=Count('casecomment', distinct=True),
        timeline_count=Count('casehistory', distinct=True),
    )


class CaseSummaryAPIView(APIView):
    """GET /api/complaints-cases/summary - open_count, total_count, closed_count."""
    permission_classes = [AllowAny]

    def get(self, request):
        total_count = Case.objects.count()
        closed_count = Case.objects.filter(cs_status__iexact='Closed').count()
        open_count = total_count - closed_count
        data = {
            'open_count': open_count,
            'total_count': total_count,
            'closed_count': closed_count,
        }
        serializer = CaseSummarySerializer(data)
        return APIResponse.success(
            data=serializer.data,
            message='Summary retrieved successfully',
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
            description='Page number',
            required=False,
        ),
        OpenApiParameter(
            name='page_size',
            type=int,
            location=OpenApiParameter.QUERY,
            description='Page size (max 100)',
            required=False,
        ),
    ],
)
class CaseListAPIView(APIView):
    """GET /api/complaints-cases - list with filters, ordering, pagination."""
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
                'status': [f'Invalid status. Allowed: {", ".join(STATUS_CHOICES)}'],
            })
        order_field = ORDERING_MAP.get(ordering_param)
        if not order_field:
            raise ValidationError({
                'ordering': [
                    'Invalid ordering. Allowed: opened_at, -opened_at, '
                    'last_modified, -last_modified',
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

        paginator = StandardPagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = CaseListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class CaseDetailAPIView(APIView):
    """GET /api/complaints-cases/{case_id} - single case with counts."""
    permission_classes = [AllowAny]

    def get(self, request, case_id):
        qs = _cases_queryset_with_counts()
        try:
            case = qs.get(cs_sf_id=case_id)
        except Case.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound('Case not found.')
        serializer = CaseDetailSerializer(case)
        return APIResponse.success(
            data=serializer.data,
            message='Case retrieved successfully',
        )


class CaseCommentsAPIView(APIView):
    """GET /api/complaints-cases/{case_id}/comments - comments latest first."""
    permission_classes = [AllowAny]

    def get(self, request, case_id):
        try:
            Case.objects.get(cs_sf_id=case_id)
        except Case.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound('Case not found.')

        comments = (
            CaseComment.objects.filter(cc_case_id_id=case_id)
            .select_related('cc_sf_created_by_id')
            .order_by('-cc_id')
        )
        serializer = CaseCommentSerializer(comments, many=True)
        return APIResponse.success(
            data=serializer.data,
            message='Comments retrieved successfully',
        )


class CaseTimelineAPIView(APIView):
    """GET /api/complaints-cases/{case_id}/timeline - case history latest first."""
    permission_classes = [AllowAny]

    def get(self, request, case_id):
        try:
            Case.objects.get(cs_sf_id=case_id)
        except Case.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound('Case not found.')

        events = (
            CaseHistory.objects.filter(ch_case_id_id=case_id)
            .select_related('ch_created_by_id')
            .order_by('-ch_created_date')
        )
        serializer = CaseTimelineSerializer(events, many=True)
        return APIResponse.success(
            data=serializer.data,
            message='Timeline retrieved successfully',
        )
