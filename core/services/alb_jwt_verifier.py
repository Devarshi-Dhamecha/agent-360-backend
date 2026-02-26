"""
ALB JWT Verification Service
Verifies JWT tokens signed by AWS ALB using ES256 algorithm.
Implements LRU caching for public keys to improve performance.
"""
import json
import logging
import time
from functools import lru_cache
from typing import Dict, Optional, Any
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

import jwt
from jwt.exceptions import (
    InvalidTokenError,
    ExpiredSignatureError,
    InvalidSignatureError,
    DecodeError
)

from core.config.alb_settings import alb_settings

logger = logging.getLogger(__name__)


class ALBJWTVerificationError(Exception):
    """Base exception for ALB JWT verification errors"""
    pass


class ALBJWTVerifier:
    """
    Service for verifying AWS ALB OIDC JWT tokens.
    Uses LRU cache to store fetched public keys for performance.
    """
    
    # Class-level cache for public keys with timestamp
    _key_cache: Dict[str, tuple[str, float]] = {}
    
    @classmethod
    def _get_cached_public_key(cls, kid: str) -> Optional[str]:
        """
        Get public key from cache if not expired.
        
        Args:
            kid: Key ID from JWT header
            
        Returns:
            Public key string if cached and not expired, None otherwise
        """
        if kid in cls._key_cache:
            key, timestamp = cls._key_cache[kid]
            ttl = alb_settings.get_cache_ttl()
            if time.time() - timestamp < ttl:
                logger.debug(f"Using cached public key for kid: {kid}")
                return key
            else:
                logger.debug(f"Cached key expired for kid: {kid}")
                del cls._key_cache[kid]
        return None
    
    @classmethod
    def _cache_public_key(cls, kid: str, public_key: str) -> None:
        """
        Cache public key with current timestamp.
        Implements simple LRU by removing oldest entry if cache is full.
        
        Args:
            kid: Key ID from JWT header
            public_key: Public key string to cache
        """
        max_size = alb_settings.get_cache_max_size()
        
        # Simple LRU: remove oldest entry if cache is full
        if len(cls._key_cache) >= max_size:
            oldest_kid = min(cls._key_cache.keys(), 
                           key=lambda k: cls._key_cache[k][1])
            del cls._key_cache[oldest_kid]
            logger.debug(f"Removed oldest cached key: {oldest_kid}")
        
        cls._key_cache[kid] = (public_key, time.time())
        logger.debug(f"Cached public key for kid: {kid}")
    
    @classmethod
    def _fetch_public_key(cls, kid: str) -> str:
        """
        Fetch public key from ALB public key endpoint.
        
        Args:
            kid: Key ID from JWT header
            
        Returns:
            Public key string
            
        Raises:
            ALBJWTVerificationError: If key cannot be fetched
        """
        # Check cache first
        cached_key = cls._get_cached_public_key(kid)
        if cached_key:
            return cached_key
        
        # Fetch from ALB endpoint
        url = alb_settings.get_public_key_url(kid)
        logger.info(f"Fetching public key from: {url}")
        
        try:
            with urlopen(url, timeout=5) as response:
                public_key = response.read().decode('utf-8')
                
            # Cache the fetched key
            cls._cache_public_key(kid, public_key)
            return public_key
            
        except HTTPError as e:
            logger.error(f"HTTP error fetching public key: {e.code} - {e.reason}")
            raise ALBJWTVerificationError(
                f"Failed to fetch public key: HTTP {e.code}"
            )
        except URLError as e:
            logger.error(f"URL error fetching public key: {e.reason}")
            raise ALBJWTVerificationError(
                f"Failed to fetch public key: {e.reason}"
            )
        except Exception as e:
            logger.error(f"Unexpected error fetching public key: {str(e)}")
            raise ALBJWTVerificationError(
                f"Failed to fetch public key: {str(e)}"
            )
    
    @classmethod
    def verify_token(cls, token: str) -> Dict[str, Any]:
        """
        Verify ALB JWT token and return claims.
        
        Args:
            token: JWT token string from x-amzn-oidc-data header
            
        Returns:
            Dictionary containing verified JWT claims
            
        Raises:
            ALBJWTVerificationError: If token verification fails
        """
        try:
            # Decode header without verification to get kid
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get('kid')
            
            if not kid:
                raise ALBJWTVerificationError("Missing 'kid' in JWT header")
            
            logger.debug(f"Verifying token with kid: {kid}")
            
            # Fetch public key
            public_key = cls._fetch_public_key(kid)
            
            # Verify token with ES256 algorithm
            claims = jwt.decode(
                token,
                public_key,
                algorithms=['ES256'],
                options={
                    'verify_signature': True,
                    'verify_exp': True,
                    'require_exp': True,
                }
            )
            
            logger.info(f"Successfully verified token for user: {claims.get('email')}")
            return claims
            
        except ExpiredSignatureError:
            logger.warning("Token has expired")
            raise ALBJWTVerificationError("Token has expired")
            
        except InvalidSignatureError:
            logger.error("Invalid token signature")
            raise ALBJWTVerificationError("Invalid token signature")
            
        except DecodeError as e:
            logger.error(f"Token decode error: {str(e)}")
            raise ALBJWTVerificationError(f"Invalid token format: {str(e)}")
            
        except InvalidTokenError as e:
            logger.error(f"Invalid token: {str(e)}")
            raise ALBJWTVerificationError(f"Invalid token: {str(e)}")
            
        except Exception as e:
            logger.error(f"Unexpected error verifying token: {str(e)}")
            raise ALBJWTVerificationError(f"Token verification failed: {str(e)}")
    
    @classmethod
    def extract_user_info(cls, claims: Dict[str, Any]) -> Dict[str, Optional[str]]:
        """
        Extract user information from verified JWT claims.
        
        Args:
            claims: Verified JWT claims dictionary
            
        Returns:
            Dictionary with user information (email, sub, given_name, family_name)
        """
        return {
            'email': claims.get('email'),
            'sub': claims.get('sub'),
            'given_name': claims.get('given_name'),
            'family_name': claims.get('family_name'),
        }
    
    @classmethod
    def clear_cache(cls) -> None:
        """Clear the public key cache. Useful for testing."""
        cls._key_cache.clear()
        logger.info("Cleared public key cache")
