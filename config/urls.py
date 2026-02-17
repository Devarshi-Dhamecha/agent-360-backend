"""
URL configuration for agent-360-backend project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/analytics/', include('apps.products.analytics.urls')),
]
