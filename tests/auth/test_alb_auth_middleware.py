"""
Unit tests for ALB Authentication Middleware
"""
from unittest.mock import patch, MagicMock
from django.test import TestCase, RequestFactory
from django.http import JsonResponse

from core.middleware.alb_auth_middleware import ALBAuthMiddleware
from core.services.alb_jwt_verifier import ALBJWTVerificationError
from apps.users.models import User, UserLoginLog


class ALBAuthMiddlewareTestCase(TestCase):
    """Test cases for ALB authentication middleware"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.factory = RequestFactory()
        self.get_response = MagicMock()
        self.middleware = ALBAuthMiddleware(self.get_response)
        
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
            usr_federation_id='azure-ad-user-123',
            usr_country='US',
            usr_time_zone='America/New_York',
            usr_language='en_US',
            usr_sf_created_date='2024-01-01T00:00:00Z',
            usr_last_modified_date='2024-01-01T00:00:00Z',
            usr_last_modified_by_id='TEST123456789012'
        )
        
        # Sample JWT claims
        self.sample_claims = {
            'sub': 'azure-ad-user-123',
            'email': 'test@example.com',
            'given_name': 'Test',
            'family_name': 'User',
        }
    
    def tearDown(self):
        """Clean up after tests"""
        User.objects.all().delete()
        UserLoginLog.objects.all().delete()
    
    @patch('core.config.alb_settings.alb_settings.is_enabled', return_value=False)
    def test_middleware_disabled(self, mock_is_enabled):
        """Test middleware bypasses when ALB auth is disabled"""
        request = self.factory.get('/api/accounts/')
        
        response = self.middleware.process_request(request)
        
        # Should return None (bypass)
        self.assertIsNone(response)
    
    @patch('core.config.alb_settings.alb_settings.is_enabled', return_value=True)
    def test_exempt_path_health(self, mock_is_enabled):
        """Test that health endpoint is exempt from authentication"""
        request = self.factory.get('/api/health/')
        
        response = self.middleware.process_request(request)
        
        # Should return None (bypass)
        self.assertIsNone(response)
    
    @patch('core.config.alb_settings.alb_settings.is_enabled', return_value=True)
    def test_missing_token(self, mock_is_enabled):
        """Test request without JWT token returns 401"""
        request = self.factory.get('/api/accounts/')
        
        response = self.middleware.process_request(request)
        
        # Should return 401
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 401)
        
        # Check response content
        content = response.content.decode('utf-8')
        self.assertIn('MISSING_AUTH_TOKEN', content)
    
    @patch('core.config.alb_settings.alb_settings.is_enabled', return_value=True)
    @patch('core.services.alb_jwt_verifier.ALBJWTVerifier.verify_token')
    def test_invalid_token(self, mock_verify, mock_is_enabled):
        """Test request with invalid JWT token returns 401"""
        mock_verify.side_effect = ALBJWTVerificationError('Invalid token')
        
        request = self.factory.get('/api/accounts/')
        request.META['HTTP_X_AMZN_OIDC_DATA'] = 'invalid.jwt.token'
        
        response = self.middleware.process_request(request)
        
        # Should return 401
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 401)
        
        # Check response content
        content = response.content.decode('utf-8')
        self.assertIn('INVALID_AUTH_TOKEN', content)
    
    @patch('core.config.alb_settings.alb_settings.is_enabled', return_value=True)
    @patch('core.services.alb_jwt_verifier.ALBJWTVerifier.verify_token')
    @patch('core.services.alb_jwt_verifier.ALBJWTVerifier.extract_user_info')
    def test_missing_email_claim(self, mock_extract, mock_verify, mock_is_enabled):
        """Test token without email claim returns 401"""
        mock_verify.return_value = self.sample_claims
        mock_extract.return_value = {'email': None, 'sub': 'test-sub'}
        
        request = self.factory.get('/api/accounts/')
        request.META['HTTP_X_AMZN_OIDC_DATA'] = 'valid.jwt.token'
        
        response = self.middleware.process_request(request)
        
        # Should return 401
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 401)
        
        # Check response content
        content = response.content.decode('utf-8')
        self.assertIn('MISSING_EMAIL_CLAIM', content)
    
    @patch('core.config.alb_settings.alb_settings.is_enabled', return_value=True)
    @patch('core.services.alb_jwt_verifier.ALBJWTVerifier.verify_token')
    @patch('core.services.alb_jwt_verifier.ALBJWTVerifier.extract_user_info')
    def test_user_not_found(self, mock_extract, mock_verify, mock_is_enabled):
        """Test token with non-existent user returns 403"""
        mock_verify.return_value = self.sample_claims
        mock_extract.return_value = {
            'email': 'nonexistent@example.com',
            'sub': 'unknown-sub',
            'given_name': 'Unknown',
            'family_name': 'User'
        }
        
        request = self.factory.get('/api/accounts/')
        request.META['HTTP_X_AMZN_OIDC_DATA'] = 'valid.jwt.token'
        
        response = self.middleware.process_request(request)
        
        # Should return 403
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 403)
        
        # Check response content
        content = response.content.decode('utf-8')
        self.assertIn('USER_NOT_FOUND', content)
    
    @patch('core.config.alb_settings.alb_settings.is_enabled', return_value=True)
    @patch('core.services.alb_jwt_verifier.ALBJWTVerifier.verify_token')
    @patch('core.services.alb_jwt_verifier.ALBJWTVerifier.extract_user_info')
    def test_successful_authentication_by_email(self, mock_extract, mock_verify, mock_is_enabled):
        """Test successful authentication by email"""
        mock_verify.return_value = self.sample_claims
        mock_extract.return_value = {
            'email': 'test@example.com',
            'sub': 'azure-ad-user-123',
            'given_name': 'Test',
            'family_name': 'User'
        }
        
        request = self.factory.get('/api/accounts/')
        request.META['HTTP_X_AMZN_OIDC_DATA'] = 'valid.jwt.token'
        request.session = {}
        
        response = self.middleware.process_request(request)
        
        # Should return None (success)
        self.assertIsNone(response)
        
        # User should be attached to request
        self.assertEqual(request.user, self.test_user)
        self.assertEqual(request.alb_claims, self.sample_claims)
    
    @patch('core.config.alb_settings.alb_settings.is_enabled', return_value=True)
    @patch('core.services.alb_jwt_verifier.ALBJWTVerifier.verify_token')
    @patch('core.services.alb_jwt_verifier.ALBJWTVerifier.extract_user_info')
    def test_successful_authentication_by_federation_id(self, mock_extract, mock_verify, mock_is_enabled):
        """Test successful authentication by federation ID"""
        mock_verify.return_value = self.sample_claims
        mock_extract.return_value = {
            'email': 'different@example.com',  # Different email
            'sub': 'azure-ad-user-123',  # But matching federation ID
            'given_name': 'Test',
            'family_name': 'User'
        }
        
        request = self.factory.get('/api/accounts/')
        request.META['HTTP_X_AMZN_OIDC_DATA'] = 'valid.jwt.token'
        request.session = {}
        
        response = self.middleware.process_request(request)
        
        # Should return None (success)
        self.assertIsNone(response)
        
        # User should be attached to request
        self.assertEqual(request.user, self.test_user)
    
    @patch('core.config.alb_settings.alb_settings.is_enabled', return_value=True)
    @patch('core.services.alb_jwt_verifier.ALBJWTVerifier.verify_token')
    @patch('core.services.alb_jwt_verifier.ALBJWTVerifier.extract_user_info')
    def test_login_logging(self, mock_extract, mock_verify, mock_is_enabled):
        """Test that login is logged on first request"""
        mock_verify.return_value = self.sample_claims
        mock_extract.return_value = {
            'email': 'test@example.com',
            'sub': 'azure-ad-user-123',
            'given_name': 'Test',
            'family_name': 'User'
        }
        
        request = self.factory.get('/api/accounts/')
        request.META['HTTP_X_AMZN_OIDC_DATA'] = 'valid.jwt.token'
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        request.META['HTTP_USER_AGENT'] = 'Test Browser'
        request.session = {}
        
        # First request - should log
        response = self.middleware.process_request(request)
        self.assertIsNone(response)
        
        # Check login log was created
        log_count = UserLoginLog.objects.filter(
            ull_user_sf_id=self.test_user
        ).count()
        self.assertEqual(log_count, 1)
        
        # Second request - should not log again
        response = self.middleware.process_request(request)
        self.assertIsNone(response)
        
        # Log count should still be 1
        log_count = UserLoginLog.objects.filter(
            ull_user_sf_id=self.test_user
        ).count()
        self.assertEqual(log_count, 1)
    
    def test_get_client_ip_with_x_forwarded_for(self):
        """Test extracting client IP from X-Forwarded-For header"""
        request = self.factory.get('/api/accounts/')
        request.META['HTTP_X_FORWARDED_FOR'] = '203.0.113.1, 198.51.100.1'
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        
        ip = self.middleware._get_client_ip(request)
        
        # Should return first IP in X-Forwarded-For
        self.assertEqual(ip, '203.0.113.1')
    
    def test_get_client_ip_without_x_forwarded_for(self):
        """Test extracting client IP from REMOTE_ADDR"""
        request = self.factory.get('/api/accounts/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        
        ip = self.middleware._get_client_ip(request)
        
        # Should return REMOTE_ADDR
        self.assertEqual(ip, '192.168.1.1')
