"""
Pagination Utilities

Provides custom pagination classes for API responses.
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from ..responses import APIResponse


class StandardPagination(PageNumberPagination):
    """
    Standard pagination for API endpoints
    
    Default: 20 items per page, max 100
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'
    
    def get_paginated_response(self, data):
        """Return paginated response in standardized format"""
        return APIResponse.paginated(
            data=data,
            page=self.page.number,
            page_size=self.page.paginator.per_page,
            total_count=self.page.paginator.count,
            message="Data retrieved successfully"
        )


class LargePagination(PageNumberPagination):
    """
    Pagination for large datasets
    
    Default: 50 items per page, max 200
    """
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200
    page_query_param = 'page'
    
    def get_paginated_response(self, data):
        return APIResponse.paginated(
            data=data,
            page=self.page.number,
            page_size=self.page.paginator.per_page,
            total_count=self.page.paginator.count,
            message="Data retrieved successfully"
        )


class SmallPagination(PageNumberPagination):
    """
    Pagination for small datasets
    
    Default: 10 items per page, max 50
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
    page_query_param = 'page'
    
    def get_paginated_response(self, data):
        return APIResponse.paginated(
            data=data,
            page=self.page.number,
            page_size=self.page.paginator.per_page,
            total_count=self.page.paginator.count,
            message="Data retrieved successfully"
        )
