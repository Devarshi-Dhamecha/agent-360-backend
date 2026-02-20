"""
Product API URL routes.
"""
from django.urls import path

from . import views

app_name = "products"

urlpatterns = [
    path(
        "performance/",
        views.ProductPerformanceAPIView.as_view(),
        name="performance",
    ),
]
