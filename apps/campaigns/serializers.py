"""
Campaign & Task API serializers.
"""
from rest_framework import serializers

from .models import Campaign, Task


class TaskListSerializer(serializers.ModelSerializer):
    """Task representation in campaign/task list responses."""

    id = serializers.CharField(source="tsk_sf_id", read_only=True)
    subject = serializers.CharField(source="tsk_subject", read_only=True)
    status = serializers.CharField(source="tsk_status", read_only=True)
    priority = serializers.CharField(source="tsk_priority", read_only=True)
    activity_date = serializers.DateField(
        source="tsk_activity_date",
        read_only=True,
    )
    owner_id = serializers.SerializerMethodField()
    campaign_id = serializers.CharField(source="tsk_what_id_id", read_only=True)
    what_id = serializers.CharField(source="tsk_what_id_id", read_only=True)
    what_type = serializers.CharField(source="tsk_what_type", read_only=True)
    what_name = serializers.CharField(source="tsk_what_name", read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "subject",
            "status",
            "priority",
            "activity_date",
            "owner_id",
            "campaign_id",
            "what_id",
            "what_type",
            "what_name",
        ]

    def get_owner_id(self, obj):
        return obj.tsk_owner_id_id if obj.tsk_owner_id_id else None


class CampaignWithTasksSerializer(serializers.ModelSerializer):
    """Campaign representation including mapped tasks."""

    id = serializers.CharField(source="cmp_sf_id", read_only=True)
    name = serializers.CharField(source="cmp_name", read_only=True)
    status = serializers.CharField(source="cmp_status", read_only=True)
    type = serializers.CharField(source="cmp_type", read_only=True)
    start_date = serializers.DateField(
        source="cmp_start_date",
        read_only=True,
    )
    end_date = serializers.DateField(
        source="cmp_end_date",
        read_only=True,
    )
    owner_id = serializers.SerializerMethodField()
    account_id = serializers.SerializerMethodField()
    is_active = serializers.BooleanField(source="cmp_is_active", read_only=True)
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = [
            "id",
            "name",
            "status",
            "type",
            "start_date",
            "end_date",
            "owner_id",
            "account_id",
            "is_active",
            "tasks",
        ]

    def get_owner_id(self, obj):
        return obj.cmp_owner_id_id if obj.cmp_owner_id_id else None

    def get_account_id(self, obj):
        return obj.cmp_account_id_id if obj.cmp_account_id_id else None

    def get_tasks(self, obj):
        """
        Return pre-fetched/mapped tasks for this campaign.

        The view is expected to provide a ``tasks_by_campaign`` mapping in the
        serializer context to avoid N+1 queries.
        """
        tasks_by_campaign = self.context.get("tasks_by_campaign", {})
        campaign_tasks = tasks_by_campaign.get(obj.cmp_sf_id, [])
        serializer = TaskListSerializer(campaign_tasks, many=True)
        return serializer.data

