"""
Unit tests for Authentication Views
"""
from django.test import TestCase, RequestFactory
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.users.auth_views import logout_view, health_check
from apps.users.models import User


class AuthViewsTestCase(TestCase):
    """Test cases for authentication views"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.factory = APIRequestFactory()
        
        # Create test user
        self.test_user = User.objects.create(
            usr_sf_id='TEST123456789012',
            usr_username='testuser',
            usr_email='test@example.com',
            usr_first_name='Test',
            usr_last_name='User',
            usr_name='Test User',
            usr_is_active=True,
            usr_active=1,
            usr_country='US',
            usr_time_zone='America/New_York',
            usr_language='en_US',
            usr_sf_created_date='2024-01-01T00:00:00Z',
            usr_last_modified_date='2024-01-01T00:00:00Z',
            usr_last_modified_by_id='TEST123456789012'
        )
    
    def tearDown(self):
        """Clean up after tests"""
        User.objects.all().delete()
    
    def test_health_check_no_auth(self):
        """Test health check endpoint without authentication"""
        request = self.factory.get('/api/health/')
        
        response = health_check(request)
        
        # Should return 200
        self.assertEqual(response.status_code, 200)
        
        # Check response data
        self.assertEqual(response.data['status'], 'healthy')
        self.assertEqual(response.data['service'], 'agent360-backend')
    
    def test_logout_authenticated(self):
        """Test logout endpoint with authenticated user"""
        request = self.factory.post('/api/auth/logout/')
        force_authenticate(request, user=self.test_user)
        
        response = logout_view(request)
        
        # Should return 200
        self.assertEqual(response.status_code, 200)
        
        # Check response data
        self.assertTrue(response.data['success'])
        self.assertIn('Logged out', response.data['message'])
        
        # Check that cookies are set to be deleted
        cookies = response.cookies
        self.assertIn('AWSELBAuthSessionCookie-0', cookies)
        
        # Check cookie is set to expire
        cookie = cookies['AWSELBAuthSessionCookie-0']
        self.assertEqual(cookie['max-age'], 0)
        self.assertEqual(cookie['expires'], 'Thu, 01 Jan 1970 00:00:00 GMT')
    
    def test_logout_clears_multiple_cookies(self):
        """Test that logout clears all ALB session cookie fragments"""
        request = self.factory.post('/api/auth/logout/')
        force_authenticate(request, user=self.test_user)
        
        response = logout_view(request)
        
        # Check that multiple cookie fragments are cleared
        cookies = response.cookies
        for i in range(5):
            cookie_name = f'AWSELBAuthSessionCookie-{i}'
            self.assertIn(cookie_name, cookies)
            self.assertEqual(cookies[cookie_name]['max-age'], 0)
