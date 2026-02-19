"""
Complaints & Cases API URL routes.
"""
from django.urls import path

from . import views

app_name = 'cases'

urlpatterns = [
    path('summary/', views.CaseSummaryAPIView.as_view(), name='summary'),
    path('', views.CaseListAPIView.as_view(), name='list'),
    path('<str:case_id>/', views.CaseDetailAPIView.as_view(), name='detail'),
    path('<str:case_id>/comments/', views.CaseCommentsAPIView.as_view(), name='comments'),
    path('<str:case_id>/timeline/', views.CaseTimelineAPIView.as_view(), name='timeline'),
]
