"""
Complaints & Cases API tests.
"""
from datetime import datetime, timezone
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from apps.users.models import User
from apps.accounts.models import Account
from .models import Case, CaseComment, CaseHistory


def _dt(year, month, day, hour=0, minute=0):
    return datetime(year, month, day, hour, minute, tzinfo=timezone.utc)


class CaseSummaryAPITests(TestCase):
    """GET /api/complaints-cases/summary"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            usr_sf_id='usr001',
            usr_username='testuser',
            usr_email='test@example.com',
            usr_last_name='User',
            usr_name='Test User',
            usr_is_active=True,
            usr_time_zone='UTC',
            usr_language='en',
            usr_sf_created_date=_dt(2020, 1, 1),
            usr_last_modified_date=_dt(2020, 1, 1),
            usr_last_modified_by_id='usr001',
        )
        self.account = Account.objects.create(
            acc_sf_id='acc001',
            acc_name='Test Account',
            acc_owner_id=self.user,
            acc_last_modified_date=_dt(2020, 1, 1),
            acc_last_modified_by_id='usr001',
        )

    def test_summary_counts(self):
        Case.objects.create(
            cs_sf_id='case1',
            cs_case_number='00001001',
            cs_subject='Open case',
            cs_status='Open',
            cs_account_id=self.account,
            cs_owner_id=self.user,
            cs_sf_created_date=_dt(2024, 1, 15),
            cs_last_modified_date=_dt(2024, 1, 15),
            cs_last_modified_by_id='usr001',
        )
        Case.objects.create(
            cs_sf_id='case2',
            cs_case_number='00001002',
            cs_subject='Closed case',
            cs_status='Closed',
            cs_account_id=self.account,
            cs_owner_id=self.user,
            cs_sf_created_date=_dt(2024, 1, 10),
            cs_last_modified_date=_dt(2024, 1, 12),
            cs_last_modified_by_id='usr001',
        )
        response = self.client.get(
            '/api/complaints-cases/summary/',
            {'account_id': self.account.acc_sf_id},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data.get('success'))
        self.assertEqual(data['data']['open_count'], 1)
        self.assertEqual(data['data']['closed_count'], 1)
        self.assertEqual(data['data']['total_count'], 2)

    def test_summary_requires_account_id(self):
        response = self.client.get('/api/complaints-cases/summary/')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_summary_counts_filtered_by_account_id(self):
        other_account = Account.objects.create(
            acc_sf_id='acc002',
            acc_name='Other Account',
            acc_owner_id=self.user,
            acc_last_modified_date=_dt(2020, 1, 1),
            acc_last_modified_by_id='usr001',
        )
        Case.objects.create(
            cs_sf_id='case_acc_1',
            cs_case_number='00001003',
            cs_subject='Open case for account 1',
            cs_status='Open',
            cs_account_id=self.account,
            cs_owner_id=self.user,
            cs_sf_created_date=_dt(2024, 1, 15),
            cs_last_modified_date=_dt(2024, 1, 15),
            cs_last_modified_by_id='usr001',
        )
        Case.objects.create(
            cs_sf_id='case_acc_2',
            cs_case_number='00001004',
            cs_subject='Closed case for account 2',
            cs_status='Closed',
            cs_account_id=other_account,
            cs_owner_id=self.user,
            cs_sf_created_date=_dt(2024, 1, 16),
            cs_last_modified_date=_dt(2024, 1, 16),
            cs_last_modified_by_id='usr001',
        )

        response = self.client.get(
            '/api/complaints-cases/summary/',
            {'account_id': self.account.acc_sf_id},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data.get('success'))
        self.assertEqual(data['data']['open_count'], 1)
        self.assertEqual(data['data']['closed_count'], 0)
        self.assertEqual(data['data']['total_count'], 1)


class CaseListAPITests(TestCase):
    """GET /api/complaints-cases - filtering by status."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            usr_sf_id='usr001',
            usr_username='testuser',
            usr_email='test@example.com',
            usr_last_name='User',
            usr_name='Test User',
            usr_is_active=True,
            usr_time_zone='UTC',
            usr_language='en',
            usr_sf_created_date=_dt(2020, 1, 1),
            usr_last_modified_date=_dt(2020, 1, 1),
            usr_last_modified_by_id='usr001',
        )
        self.account = Account.objects.create(
            acc_sf_id='acc001',
            acc_name='Test Account',
            acc_owner_id=self.user,
            acc_last_modified_date=_dt(2020, 1, 1),
            acc_last_modified_by_id='usr001',
        )
        self.case_open = Case.objects.create(
            cs_sf_id='case_open',
            cs_case_number='00002001',
            cs_subject='An open case',
            cs_status='Open',
            cs_account_id=self.account,
            cs_owner_id=self.user,
            cs_sf_created_date=_dt(2024, 2, 1),
            cs_last_modified_date=_dt(2024, 2, 1),
            cs_last_modified_by_id='usr001',
        )
        self.case_closed = Case.objects.create(
            cs_sf_id='case_closed',
            cs_case_number='00002002',
            cs_subject='A closed case',
            cs_status='Closed',
            cs_account_id=self.account,
            cs_owner_id=self.user,
            cs_sf_created_date=_dt(2024, 2, 2),
            cs_last_modified_date=_dt(2024, 2, 3),
            cs_last_modified_by_id='usr001',
        )

    def test_list_filter_status_open(self):
        response = self.client.get('/api/complaints-cases/', {'status': 'open'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data.get('success'))
        results = data['data']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], 'case_open')
        self.assertEqual(results[0]['status'], 'Open')

    def test_list_filter_status_closed(self):
        response = self.client.get('/api/complaints-cases/', {'status': 'closed'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json()['data']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], 'case_closed')

    def test_list_invalid_status_returns_400(self):
        response = self.client.get('/api/complaints-cases/', {'status': 'invalid'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_invalid_ordering_returns_400(self):
        response = self.client.get('/api/complaints-cases/', {'ordering': 'invalid'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CaseDetailAPITests(TestCase):
    """GET /api/complaints-cases/{case_id} - detail and 404."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            usr_sf_id='usr001',
            usr_username='testuser',
            usr_email='test@example.com',
            usr_last_name='User',
            usr_name='Test User',
            usr_is_active=True,
            usr_time_zone='UTC',
            usr_language='en',
            usr_sf_created_date=_dt(2020, 1, 1),
            usr_last_modified_date=_dt(2020, 1, 1),
            usr_last_modified_by_id='usr001',
        )
        self.account = Account.objects.create(
            acc_sf_id='acc001',
            acc_name='Test Account',
            acc_owner_id=self.user,
            acc_last_modified_date=_dt(2020, 1, 1),
            acc_last_modified_by_id='usr001',
        )
        self.case = Case.objects.create(
            cs_sf_id='case_detail_1',
            cs_case_number='00003001',
            cs_subject='Detail case',
            cs_description='Some description',
            cs_status='Working',
            cs_account_id=self.account,
            cs_owner_id=self.user,
            cs_sf_created_date=_dt(2024, 3, 1),
            cs_last_modified_date=_dt(2024, 3, 2),
            cs_last_modified_by_id='usr001',
        )

    def test_detail_found(self):
        response = self.client.get('/api/complaints-cases/case_detail_1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data.get('success'))
        self.assertEqual(data['data']['id'], 'case_detail_1')
        self.assertEqual(data['data']['case_number'], '00003001')
        self.assertEqual(data['data']['title'], 'Detail case')
        self.assertEqual(data['data']['description'], 'Some description')
        self.assertEqual(data['data']['status'], 'Working')
        self.assertIn('comments_count', data['data'])
        self.assertIn('timeline_count', data['data'])

    def test_detail_not_found_returns_404(self):
        response = self.client.get('/api/complaints-cases/nonexistent_id_xyz/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CaseCommentsAndTimelineAPITests(TestCase):
    """GET comments and timeline - counts, ordering, 404."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            usr_sf_id='usr001',
            usr_username='testuser',
            usr_email='test@example.com',
            usr_last_name='User',
            usr_name='Test User',
            usr_is_active=True,
            usr_time_zone='UTC',
            usr_language='en',
            usr_sf_created_date=_dt(2020, 1, 1),
            usr_last_modified_date=_dt(2020, 1, 1),
            usr_last_modified_by_id='usr001',
        )
        self.account = Account.objects.create(
            acc_sf_id='acc001',
            acc_name='Test Account',
            acc_owner_id=self.user,
            acc_last_modified_date=_dt(2020, 1, 1),
            acc_last_modified_by_id='usr001',
        )
        self.case = Case.objects.create(
            cs_sf_id='case_comments_1',
            cs_case_number='00004001',
            cs_subject='Case with comments',
            cs_status='Open',
            cs_account_id=self.account,
            cs_owner_id=self.user,
            cs_sf_created_date=_dt(2024, 4, 1),
            cs_last_modified_date=_dt(2024, 4, 1),
            cs_last_modified_by_id='usr001',
        )

    def test_comments_count_and_ordering(self):
        CaseComment.objects.create(
            cc_case_id=self.case,
            cc_comment_body='First comment',
            cc_sf_created_by_id=self.user,
            cc_sf_created_date=_dt(2024, 4, 1, 10, 0),
        )
        CaseComment.objects.create(
            cc_case_id=self.case,
            cc_comment_body='Second comment',
            cc_sf_created_by_id=self.user,
            cc_sf_created_date=_dt(2024, 4, 1, 11, 0),
        )
        response = self.client.get(f'/api/complaints-cases/{self.case.cs_sf_id}/comments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data.get('success'))
        comments = data['data']
        self.assertEqual(len(comments), 2)
        self.assertEqual(comments[0]['body'], 'Second comment')
        self.assertEqual(comments[1]['body'], 'First comment')
        self.assertIn('created_by_name', comments[0])

    def test_timeline_count_and_ordering(self):
        CaseHistory.objects.create(
            ch_sf_id='ch001',
            ch_case_id=self.case,
            ch_field='Status',
            ch_old_value='New',
            ch_new_value='Working',
            ch_created_date=_dt(2024, 4, 1, 9, 0),
            ch_created_by_id=self.user,
        )
        CaseHistory.objects.create(
            ch_sf_id='ch002',
            ch_case_id=self.case,
            ch_field='Status',
            ch_old_value='Working',
            ch_new_value='Open',
            ch_created_date=_dt(2024, 4, 1, 10, 0),
            ch_created_by_id=self.user,
        )
        response = self.client.get(f'/api/complaints-cases/{self.case.cs_sf_id}/timeline/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data.get('success'))
        events = data['data']
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]['event_id'], 'ch002')
        self.assertEqual(events[0]['new_value'], 'Open')
        self.assertIn('created_by_name', events[0])

    def test_comments_not_found_returns_404(self):
        response = self.client.get('/api/complaints-cases/nonexistent_xyz/comments/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_timeline_not_found_returns_404(self):
        response = self.client.get('/api/complaints-cases/nonexistent_xyz/timeline/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
