"""
Complaints & Cases API serializers.
"""
from rest_framework import serializers
from django.utils import timezone

from .models import Case, CaseComment, CaseHistory


def _format_opened_display(dt):
    """Format datetime as DD/MM/YYYY for display."""
    if not dt:
        return None
    return dt.strftime('%d/%m/%Y')


def _comment_created_at(comment):
    """Best created timestamp for a comment: SF date or agent date."""
    if comment.cc_sf_created_date:
        return comment.cc_sf_created_date
    if comment.cc_agent_created_date:
        return comment.cc_agent_created_date
    return comment.cc_created_at


def _user_display_name(user):
    """Display name for a user (usr_name or first + last)."""
    if not user:
        return None
    return getattr(user, 'usr_name', None) or (
        f"{getattr(user, 'usr_first_name', '') or ''} {getattr(user, 'usr_last_name', '') or ''}".strip()
        or None
    )


class CaseSummarySerializer(serializers.Serializer):
    """Response for GET /api/complaints-cases/summary."""
    open_count = serializers.IntegerField()
    total_count = serializers.IntegerField()
    closed_count = serializers.IntegerField()


class CaseListSerializer(serializers.ModelSerializer):
    """Single case in list response."""
    id = serializers.CharField(source='cs_sf_id', read_only=True)
    case_number = serializers.CharField(source='cs_case_number', read_only=True)
    title = serializers.CharField(source='cs_subject', read_only=True)
    status = serializers.CharField(source='cs_status', read_only=True)
    opened_at = serializers.SerializerMethodField()
    opened_at_display = serializers.SerializerMethodField()
    comments_count = serializers.IntegerField(read_only=True)
    timeline_count = serializers.IntegerField(read_only=True)
    priority = serializers.CharField(source='cs_priority', read_only=True)
    account_id = serializers.SerializerMethodField()
    owner_id = serializers.SerializerMethodField()

    class Meta:
        model = Case
        fields = [
            'id', 'case_number', 'title', 'status',
            'opened_at', 'opened_at_display',
            'comments_count', 'timeline_count',
            'priority', 'account_id', 'owner_id',
        ]

    def get_opened_at(self, obj):
        if not obj.cs_sf_created_date:
            return None
        return obj.cs_sf_created_date.date().isoformat()

    def get_opened_at_display(self, obj):
        return _format_opened_display(obj.cs_sf_created_date)

    def get_account_id(self, obj):
        return obj.cs_account_id_id if hasattr(obj, 'cs_account_id_id') else None

    def get_owner_id(self, obj):
        return obj.cs_owner_id_id if hasattr(obj, 'cs_owner_id_id') else None


class CaseDetailSerializer(serializers.ModelSerializer):
    """Single case detail response."""
    id = serializers.CharField(source='cs_sf_id', read_only=True)
    case_number = serializers.CharField(source='cs_case_number', read_only=True)
    title = serializers.CharField(source='cs_subject', read_only=True)
    description = serializers.CharField(source='cs_description', read_only=True)
    status = serializers.CharField(source='cs_status', read_only=True)
    opened_at = serializers.SerializerMethodField()
    opened_at_display = serializers.SerializerMethodField()
    comments_count = serializers.IntegerField(read_only=True)
    timeline_count = serializers.IntegerField(read_only=True)
    priority = serializers.CharField(source='cs_priority', read_only=True)
    account_id = serializers.SerializerMethodField()
    owner_id = serializers.SerializerMethodField()

    class Meta:
        model = Case
        fields = [
            'id', 'case_number', 'title', 'description', 'status',
            'opened_at', 'opened_at_display',
            'comments_count', 'timeline_count',
            'priority', 'account_id', 'owner_id',
        ]

    def get_opened_at(self, obj):
        if not obj.cs_sf_created_date:
            return None
        return obj.cs_sf_created_date.date().isoformat()

    def get_opened_at_display(self, obj):
        return _format_opened_display(obj.cs_sf_created_date)

    def get_account_id(self, obj):
        return obj.cs_account_id_id if hasattr(obj, 'cs_account_id_id') else None

    def get_owner_id(self, obj):
        return obj.cs_owner_id_id if hasattr(obj, 'cs_owner_id_id') else None


class CaseCommentSerializer(serializers.ModelSerializer):
    """Single comment in comments list."""
    comment_id = serializers.IntegerField(source='cc_id', read_only=True)
    body = serializers.CharField(source='cc_comment_body', read_only=True)
    created_at = serializers.SerializerMethodField()
    created_by_id = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    is_published = serializers.BooleanField(source='cc_is_published', read_only=True)

    class Meta:
        model = CaseComment
        fields = [
            'comment_id', 'body', 'created_at',
            'created_by_id', 'created_by_name', 'is_published',
        ]

    def get_created_at(self, obj):
        dt = _comment_created_at(obj)
        if not dt:
            return None
        if timezone.is_naive(dt):
            return timezone.make_aware(dt).isoformat()
        return dt.isoformat()

    def get_created_by_id(self, obj):
        return obj.cc_sf_created_by_id_id if hasattr(obj, 'cc_sf_created_by_id_id') else None

    def get_created_by_name(self, obj):
        return _user_display_name(getattr(obj, 'cc_sf_created_by_id', None))


class CaseTimelineSerializer(serializers.ModelSerializer):
    """Single timeline event from case_history."""
    event_id = serializers.CharField(source='ch_sf_id', read_only=True)
    field = serializers.CharField(source='ch_field', read_only=True)
    old_value = serializers.CharField(source='ch_old_value', read_only=True)
    new_value = serializers.CharField(source='ch_new_value', read_only=True)
    created_at = serializers.SerializerMethodField()
    created_by_id = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = CaseHistory
        fields = [
            'event_id', 'field', 'old_value', 'new_value',
            'created_at', 'created_by_id', 'created_by_name',
        ]

    def get_created_at(self, obj):
        dt = getattr(obj, 'ch_created_date', None)
        if not dt:
            return None
        if timezone.is_naive(dt):
            return timezone.make_aware(dt).isoformat()
        return dt.isoformat()

    def get_created_by_id(self, obj):
        return obj.ch_created_by_id_id if hasattr(obj, 'ch_created_by_id_id') else None

    def get_created_by_name(self, obj):
        return _user_display_name(getattr(obj, 'ch_created_by_id', None))
