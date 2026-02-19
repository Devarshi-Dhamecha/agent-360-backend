"""
Account API views.
"""
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from core.api.responses import APIResponse
from core.api.utils.pagination import StandardPagination

from .models import Account
from .serializers import AccountListSerializer


class AccountListAPIView(APIView):
    """GET /api/accounts/ - list accounts with optional user_id (owner) filter."""
    permission_classes = [AllowAny]

    def get(self, request):
        user_id = (request.query_params.get('user_id') or '').strip()

        qs = Account.objects.select_related('acc_owner_id').all()
        if user_id:
            qs = qs.filter(acc_owner_id_id=user_id)

        qs = qs.order_by('acc_name')

        paginator = StandardPagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = AccountListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
