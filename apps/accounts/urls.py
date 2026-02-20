"""
Account API URL routes.
"""
from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.AccountListAPIView.as_view(), name='list'),
    path('user/<str:user_id>/', views.AccountsByUserAPIView.as_view(), name='by-user'),
]
