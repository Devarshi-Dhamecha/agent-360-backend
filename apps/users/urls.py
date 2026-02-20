"""
User API URL routes.
"""
from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('', views.UserListAPIView.as_view(), name='list'),
]
