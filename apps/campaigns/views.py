"""
Campaign & Task API views.
"""
from typing import Dict, List

from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from core.api.responses import ErrorResponse
from core.api.utils.pagination import StandardPagination

from .models import Campaign, Task
from .serializers import CampaignWithTasksSerializer, TaskListSerializer


class CampaignListWithTasksAPIView(APIView):
    """
    GET /api/campaigns/ - list campaigns with tasks.

    Query parameters:
    - account_id (required): Salesforce Account ID (cmp_account_id)
    - user_id (optional, required when type="my"): Salesforce User ID (tsk_owner_id)
    - type (optional): "all" | "my"
        * all (default): campaigns for the account with all tasks mapped
        * my: campaigns for the account with only tasks assigned to that user
    """

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Campaigns"],
        summary="List campaigns with mapped tasks",
        description=(
            "Returns campaigns for a given account with mapped tasks.\n\n"
            "- type=all: all tasks mapped to the campaign\n"
            "- type=my: only tasks owned by the given user (user_id required)\n\n"
            "Pagination is optional. If page or page_size parameters are provided, "
            "the response will be paginated. Otherwise, all data is returned."
        ),
        parameters=[
            OpenApiParameter(
                name="account_id",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Salesforce Account ID (cmp_account_id)",
            ),
            OpenApiParameter(
                name="user_id",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description=(
                    "Salesforce User ID (tsk_owner_id). "
                    "Required when type='my'."
                ),
            ),
            OpenApiParameter(
                name="type",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Filter type: 'all' (default) or 'my'",
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
        responses={200: CampaignWithTasksSerializer},
    )
    def get(self, request):
        account_id = (request.query_params.get("account_id") or "").strip()
        user_id = (request.query_params.get("user_id") or "").strip()
        type_param = (request.query_params.get("type") or "all").strip().lower()

        errors: List[Dict] = []

        if not account_id:
            errors.append(
                {
                    "field": "account_id",
                    "message": "account_id is required",
                }
            )

        if type_param not in {"all", "my"}:
            errors.append(
                {
                    "field": "type",
                    "message": "type must be either 'all' or 'my'",
                }
            )

        if type_param == "my" and not user_id:
            errors.append(
                {
                    "field": "user_id",
                    "message": "user_id is required when type is 'my'",
                }
            )

        if errors:
            return ErrorResponse.validation_error(
                message="Invalid query parameters",
                errors=errors,
            )

        campaigns_qs = Campaign.objects.select_related(
            "cmp_owner_id",
            "cmp_account_id",
        ).filter(
            cmp_account_id_id=account_id,
            cmp_active=1,
        ).order_by("cmp_name")

        # Check if pagination parameters are provided
        page_param = request.query_params.get('page')
        page_size_param = request.query_params.get('page_size')

        # If either pagination parameter is provided, use pagination
        if page_param is not None or page_size_param is not None:
            paginator = StandardPagination()
            page = paginator.paginate_queryset(campaigns_qs, request)
            campaign_ids = [campaign.cmp_sf_id for campaign in page]
        else:
            # Return all data without pagination
            page = list(campaigns_qs)
            campaign_ids = [campaign.cmp_sf_id for campaign in page]

        tasks_qs = Task.objects.filter(
            tsk_what_id_id__in=campaign_ids,
            tsk_active=1,
        )

        if type_param == "my":
            tasks_qs = tasks_qs.filter(tsk_owner_id_id=user_id)

        tasks_by_campaign: Dict[str, List[Task]] = {}
        for task in tasks_qs:
            cid = task.tsk_what_id_id
            if cid:
                tasks_by_campaign.setdefault(cid, []).append(task)

        serializer_context = {
            "request": request,
            "tasks_by_campaign": tasks_by_campaign,
        }

        serializer = CampaignWithTasksSerializer(
            page,
            many=True,
            context=serializer_context,
        )
        
        # Return paginated or non-paginated response
        if page_param is not None or page_size_param is not None:
            return paginator.get_paginated_response(serializer.data)
        else:
            from core.api.responses import APIResponse
            return APIResponse.success(
                data=serializer.data,
                message='Data retrieved successfully'
            )


class TaskListByCampaignAPIView(APIView):
    """
    GET /api/campaigns/tasks/ - list tasks filtered by campaign.

    Query parameters:
    - campaign_id (required): Salesforce Campaign ID (cmp_sf_id)
    """

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Campaigns"],
        summary="List tasks by campaign",
        description=(
            "Returns tasks mapped to the given Salesforce Campaign.\n\n"
            "Pagination is optional. If page or page_size parameters are provided, "
            "the response will be paginated. Otherwise, all data is returned."
        ),
        parameters=[
            OpenApiParameter(
                name="campaign_id",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Salesforce Campaign ID (cmp_sf_id)",
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
        responses={200: TaskListSerializer},
    )
    def get(self, request):
        campaign_id = (request.query_params.get("campaign_id") or "").strip()

        if not campaign_id:
            return ErrorResponse.validation_error(
                message="Invalid query parameters",
                errors=[
                    {
                        "field": "campaign_id",
                        "message": "campaign_id is required",
                    }
                ],
            )

        tasks_qs = Task.objects.filter(
            tsk_what_id_id=campaign_id,
            tsk_active=1,
        ).order_by("tsk_activity_date", "tsk_subject")

        # Check if pagination parameters are provided
        page_param = request.query_params.get('page')
        page_size_param = request.query_params.get('page_size')

        # If either pagination parameter is provided, use pagination
        if page_param is not None or page_size_param is not None:
            paginator = StandardPagination()
            page = paginator.paginate_queryset(tasks_qs, request)
            serializer = TaskListSerializer(page, many=True, context={"request": request})
            return paginator.get_paginated_response(serializer.data)
        
        # Otherwise, return all data without pagination
        serializer = TaskListSerializer(tasks_qs, many=True, context={"request": request})
        from core.api.responses import APIResponse
        return APIResponse.success(
            data=serializer.data,
            message='Data retrieved successfully'
        )

