"""
User API views.
"""
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from core.api.utils.pagination import StandardPagination

from .models import User
from .serializers import UserListSerializer


class UserListAPIView(APIView):
    """GET /api/users/ - list all users."""
    permission_classes = [AllowAny]

    def get(self, request):
        qs = User.objects.select_related('usr_user_role_id').filter(usr_active=1).order_by('usr_name')

        paginator = StandardPagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = UserListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
