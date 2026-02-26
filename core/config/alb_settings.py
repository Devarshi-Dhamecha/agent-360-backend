"""
ALB Authentication Configuration
Loads and provides typed access to ALB-related environment variables.
"""
import os
from typing import Optional


class ALBSettings:
    """Configuration for AWS ALB OIDC Authentication"""
    
    @staticmethod
    def is_enabled() -> bool:
        """Check if ALB authentication is enabled"""
        return os.getenv('ALB_AUTH_ENABLED', 'false').lower() == 'true'
    
    @staticmethod
    def get_aws_region() -> str:
        """Get AWS region for ALB public key fetching"""
        return os.getenv('AWS_REGION', 'us-east-1')
    
    @staticmethod
    def get_public_key_url(kid: str) -> str:
        """Generate ALB public key URL for given key ID"""
        region = ALBSettings.get_aws_region()
        return f"https://public-keys.auth.elb.{region}.amazonaws.com/{kid}"
    
    @staticmethod
    def get_cache_ttl() -> int:
        """Get cache TTL in seconds for public keys (default: 1 hour)"""
        return int(os.getenv('ALB_KEY_CACHE_TTL', '3600'))
    
    @staticmethod
    def get_cache_max_size() -> int:
        """Get maximum cache size for LRU cache (default: 100)"""
        return int(os.getenv('ALB_KEY_CACHE_MAX_SIZE', '100'))


# Singleton instance
alb_settings = ALBSettings()
