"""
Product API URL routes.
"""
from django.urls import path

from . import views
from . import analytics_views

app_name = "products"

urlpatterns = [
    path(
        "performance/",
        views.ProductPerformanceAPIView.as_view(),
        name="performance",
    ),
]

# Sales Analytics URLs
sales_urlpatterns = [
    path(
        "family/",
        analytics_views.ProductFamilyAnalyticsAPIView.as_view(),
        name="family_analytics",
    ),
    path(
        "product/",
        analytics_views.ProductAnalyticsAPIView.as_view(),
        name="product_analytics",
    ),
    path(
        "orders/",
        analytics_views.OrderContributionAPIView.as_view(),
        name="order_contribution",
    ),
    path(
        "order-details/",
        analytics_views.OrderDetailsAPIView.as_view(),
        name="order_details",
    ),
]
