"""
Product API URL routes.
"""
from django.urls import path

from . import views
from . import analytics_views

app_name = "products"

urlpatterns = [
    path(
        "performance/achieved/",
        views.QuarterlyPerformanceAPIView.as_view(),
        name="performance_achieved",
    ),
    path(
        "performance/deviation/",
        views.ProductDeviationPerformanceAPIView.as_view(),
        name="performance_deviation",
    ),
    path(
        "rfc-by-month/",
        views.RfcByMonthAPIView.as_view(),
        name="rfc_by_month",
    ),
    path(
        "update-rfc/",
        views.UpdateRfcAPIView.as_view(),
        name="update_rfc",
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
