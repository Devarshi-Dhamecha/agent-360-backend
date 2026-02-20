"""
Campaign & Task API URL routes.
"""
from django.urls import path

from . import views

app_name = "campaigns"

urlpatterns = [
    path(
        "",
        views.CampaignListWithTasksAPIView.as_view(),
        name="list-with-tasks",
    ),
    path(
        "tasks/",
        views.TaskListByCampaignAPIView.as_view(),
        name="tasks-by-campaign",
    ),
]

