"""
Unit tests for ALB JWT Verifier
"""
import time
from unittest.mock import patch, MagicMock
from django.test import TestCase
import jwt

from core.services.alb_jwt_verifier import (
    ALBJWTVerifier,
    ALBJWTVerificationError
)


class ALBJWTVerifierTestCase(TestCase):
    """Test cases for ALB JWT verification service"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Clear cache before each test
        ALBJWTVerifier.clear_cache()
        
        # Sample JWT claims
        self.sample_claims = {
            'sub': 'azure-ad-user-id-123',
            'email': 'test@example.com',
            'given_name': 'John',
            'family_name': 'Doe',
            'exp': int(time.time()) + 3600,  # Expires in 1 hour
        }
        
        # Sample public key (for testing)
        self.sample_public_key = """-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAETest...
-----END PUBLIC KEY-----"""
    
    def tearDown(self):
        """Clean up after tests"""
        ALBJWTVerifier.clear_cache()
    
    @patch('core.services.alb_jwt_verifier.urlopen')
    def test_fetch_public_key_success(self, mock_urlopen):
        """Test successful public key fetching"""
        # Mock response
        mock_response = MagicMock()
        mock_response.read.return_value = self.sample_public_key.encode('utf-8')
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        
        # Fetch key
        kid = 'test-key-id'
        public_key = ALBJWTVerifier._fetch_public_key(kid)
        
        # Assertions
        self.assertEqual(public_key, self.sample_public_key)
        mock_urlopen.assert_called_once()
    
    @patch('core.services.alb_jwt_verifier.urlopen')
    def test_fetch_public_key_caching(self, mock_urlopen):
        """Test that public keys are cached"""
        # Mock response
        mock_response = MagicMock()
        mock_response.read.return_value = self.sample_public_key.encode('utf-8')
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        
        kid = 'test-key-id'
        
        # First fetch - should call urlopen
        key1 = ALBJWTVerifier._fetch_public_key(kid)
        self.assertEqual(mock_urlopen.call_count, 1)
        
        # Second fetch - should use cache
        key2 = ALBJWTVerifier._fetch_public_key(kid)
        self.assertEqual(mock_urlopen.call_count, 1)  # Still 1
        
        # Keys should be the same
        self.assertEqual(key1, key2)
    
    def test_cache_expiration(self):
        """Test that cached keys expire after TTL"""
        kid = 'test-key-id'
        
        # Cache a key with timestamp in the past
        past_timestamp = time.time() - 7200  # 2 hours ago
        ALBJWTVerifier._key_cache[kid] = (self.sample_public_key, past_timestamp)
        
        # Try to get cached key - should return None (expired)
        cached_key = ALBJWTVerifier._get_cached_public_key(kid)
        self.assertIsNone(cached_key)
        
        # Cache should be cleared
        self.assertNotIn(kid, ALBJWTVerifier._key_cache)
    
    def test_cache_lru_eviction(self):
        """Test LRU eviction when cache is full"""
        # Set small max size for testing
        with patch('core.config.alb_settings.alb_settings.get_cache_max_size', return_value=3):
            # Add 3 keys
            for i in range(3):
                kid = f'key-{i}'
                ALBJWTVerifier._cache_public_key(kid, f'public-key-{i}')
            
            # Cache should have 3 keys
            self.assertEqual(len(ALBJWTVerifier._key_cache), 3)
            
            # Add 4th key - should evict oldest
            ALBJWTVerifier._cache_public_key('key-3', 'public-key-3')
            
            # Cache should still have 3 keys
            self.assertEqual(len(ALBJWTVerifier._key_cache), 3)
            
            # Oldest key should be evicted
            self.assertNotIn('key-0', ALBJWTVerifier._key_cache)
            self.assertIn('key-3', ALBJWTVerifier._key_cache)
    
    def test_extract_user_info(self):
        """Test extracting user info from claims"""
        user_info = ALBJWTVerifier.extract_user_info(self.sample_claims)
        
        self.assertEqual(user_info['email'], 'test@example.com')
        self.assertEqual(user_info['sub'], 'azure-ad-user-id-123')
        self.assertEqual(user_info['given_name'], 'John')
        self.assertEqual(user_info['family_name'], 'Doe')
    
    def test_extract_user_info_missing_fields(self):
        """Test extracting user info with missing fields"""
        claims = {'email': 'test@example.com'}
        user_info = ALBJWTVerifier.extract_user_info(claims)
        
        self.assertEqual(user_info['email'], 'test@example.com')
        self.assertIsNone(user_info['sub'])
        self.assertIsNone(user_info['given_name'])
        self.assertIsNone(user_info['family_name'])
    
    @patch('core.services.alb_jwt_verifier.jwt.decode')
    @patch('core.services.alb_jwt_verifier.jwt.get_unverified_header')
    @patch.object(ALBJWTVerifier, '_fetch_public_key')
    def test_verify_token_success(self, mock_fetch_key, mock_get_header, mock_decode):
        """Test successful token verification"""
        # Mock responses
        mock_get_header.return_value = {'kid': 'test-key-id', 'alg': 'ES256'}
        mock_fetch_key.return_value = self.sample_public_key
        mock_decode.return_value = self.sample_claims
        
        # Verify token
        token = 'fake.jwt.token'
        claims = ALBJWTVerifier.verify_token(token)
        
        # Assertions
        self.assertEqual(claims, self.sample_claims)
        mock_get_header.assert_called_once_with(token)
        mock_fetch_key.assert_called_once_with('test-key-id')
        mock_decode.assert_called_once()
    
    @patch('core.services.alb_jwt_verifier.jwt.get_unverified_header')
    def test_verify_token_missing_kid(self, mock_get_header):
        """Test token verification with missing kid"""
        mock_get_header.return_value = {'alg': 'ES256'}
        
        with self.assertRaises(ALBJWTVerificationError) as context:
            ALBJWTVerifier.verify_token('fake.jwt.token')
        
        self.assertIn('kid', str(context.exception))
    
    @patch('core.services.alb_jwt_verifier.jwt.decode')
    @patch('core.services.alb_jwt_verifier.jwt.get_unverified_header')
    @patch.object(ALBJWTVerifier, '_fetch_public_key')
    def test_verify_token_expired(self, mock_fetch_key, mock_get_header, mock_decode):
        """Test token verification with expired token"""
        from jwt.exceptions import ExpiredSignatureError
        
        mock_get_header.return_value = {'kid': 'test-key-id', 'alg': 'ES256'}
        mock_fetch_key.return_value = self.sample_public_key
        mock_decode.side_effect = ExpiredSignatureError('Token expired')
        
        with self.assertRaises(ALBJWTVerificationError) as context:
            ALBJWTVerifier.verify_token('fake.jwt.token')
        
        self.assertIn('expired', str(context.exception).lower())
    
    @patch('core.services.alb_jwt_verifier.jwt.decode')
    @patch('core.services.alb_jwt_verifier.jwt.get_unverified_header')
    @patch.object(ALBJWTVerifier, '_fetch_public_key')
    def test_verify_token_invalid_signature(self, mock_fetch_key, mock_get_header, mock_decode):
        """Test token verification with invalid signature"""
        from jwt.exceptions import InvalidSignatureError
        
        mock_get_header.return_value = {'kid': 'test-key-id', 'alg': 'ES256'}
        mock_fetch_key.return_value = self.sample_public_key
        mock_decode.side_effect = InvalidSignatureError('Invalid signature')
        
        with self.assertRaises(ALBJWTVerificationError) as context:
            ALBJWTVerifier.verify_token('fake.jwt.token')
        
        self.assertIn('signature', str(context.exception).lower())
