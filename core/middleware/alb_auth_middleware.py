"""
ALB Authentication Middleware
Validates AWS ALB OIDC JWT tokens and resolves users.
Only active when ALB_AUTH_ENABLED=true.
"""
import json
import logging
from typing import Callable, Optional

from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin
from django.utils.timezone import now
from rest_framework import status

from apps.users.models import User, UserLoginLog
from core.api.responses import ErrorResponse
from core.api.constants import ErrorMessages, ErrorCodes
from core.config.alb_settings import alb_settings
from core.services.alb_jwt_verifier import ALBJWTVerifier, ALBJWTVerificationError

logger = logging.getLogger(__name__)


class ALBAuthMiddleware(MiddlewareMixin):
    """
    Middleware to authenticate requests using AWS ALB OIDC JWT tokens.
    
    When ALB_AUTH_ENABLED=true:
    - Validates x-amzn-oidc-data header
    - Verifies JWT signature
    - Resolves user from database
    - Attaches user and claims to request
    - Logs first login of session
    
    When ALB_AUTH_ENABLED=false:
    - Bypasses all authentication (for local development)
    """
    
    # Paths that don't require authentication
    EXEMPT_PATHS = [
        '/api/health/',
        '/admin/login/',
        '/api/schema/',
        '/api/docs/',
    ]
    
    def __init__(self, get_response: Callable):
        super().__init__(get_response)
        self.get_response = get_response
        
        if alb_settings.is_enabled():
            logger.info("ALB Authentication is ENABLED")
        else:
            logger.info("ALB Authentication is DISABLED (local development mode)")
    
    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        """
        Process incoming request for ALB authentication.
        
        Args:
            request: Django HTTP request
            
        Returns:
            HttpResponse with error if authentication fails, None otherwise
        """
        # Skip if ALB auth is disabled
        if not alb_settings.is_enabled():
            logger.debug("ALB auth disabled, skipping authentication")
            return None
        
        # Check if path is exempt from authentication
        if self._is_exempt_path(request.path):
            logger.debug(f"Path {request.path} is exempt from authentication")
            return None
        
        # Extract JWT token from header
        token = request.META.get('HTTP_X_AMZN_OIDC_DATA')
        
        if not token:
            logger.warning(f"Missing x-amzn-oidc-data header for {request.path}")
            return self._render_error_response(
                message=ErrorMessages.MISSING_AUTH_TOKEN,
                error_code=ErrorCodes.MISSING_AUTH_TOKEN,
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        # Verify JWT token
        try:
            claims = ALBJWTVerifier.verify_token(token)
        except ALBJWTVerificationError as e:
            logger.error(f"JWT verification failed: {str(e)}")
            return self._render_error_response(
                message=f'{ErrorMessages.INVALID_AUTH_TOKEN}: {str(e)}',
                error_code=ErrorCodes.INVALID_AUTH_TOKEN,
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        # Extract user info from claims
        user_info = ALBJWTVerifier.extract_user_info(claims)
        email = user_info.get('email')
        sub = user_info.get('sub')
        
        if not email:
            logger.error("Missing email in JWT claims")
            return self._render_error_response(
                message=ErrorMessages.MISSING_EMAIL_CLAIM,
                error_code=ErrorCodes.MISSING_EMAIL_CLAIM,
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        # Resolve user from database
        user = self._resolve_user(email, sub)
        
        if not user:
            logger.warning(f"User not found or inactive: {email}")
            return self._render_error_response(
                message=ErrorMessages.USER_NOT_FOUND,
                error_code=ErrorCodes.USER_NOT_FOUND,
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        # Attach user and claims to request
        request.user = user
        request.alb_claims = claims
        
        # Log first login of session
        self._log_login_if_needed(request, user)
        
        logger.debug(f"Authenticated user: {user.usr_email}")
        return None
    
    def _is_exempt_path(self, path: str) -> bool:
        """Check if path is exempt from authentication"""
        return any(path.startswith(exempt) for exempt in self.EXEMPT_PATHS)
    
    def _resolve_user(self, email: str, sub: Optional[str]) -> Optional[User]:
        """
        Resolve user from database by email or federation ID.
        
        Args:
            email: User email from JWT claims
            sub: Subject (federation ID) from JWT claims
            
        Returns:
            User instance if found and active, None otherwise
        """
        try:
            # Try to find by email first
            user = User.objects.filter(
                usr_email=email,
                usr_is_active=True,
                usr_active=1
            ).first()
            
            if user:
                logger.debug(f"User found by email: {email}")
                return user
            
            # Fallback to federation ID if provided
            if sub:
                user = User.objects.filter(
                    usr_federation_id=sub,
                    usr_is_active=True,
                    usr_active=1
                ).first()
                
                if user:
                    logger.debug(f"User found by federation ID: {sub}")
                    return user
            
            logger.warning(f"No active user found for email: {email}, sub: {sub}")
            return None
            
        except Exception as e:
            logger.error(f"Error resolving user: {str(e)}")
            return None
    
    def _log_login_if_needed(self, request: HttpRequest, user: User) -> None:
        """
        Log user login if this is the first request of the session.
        
        Args:
            request: Django HTTP request
            user: Authenticated user
        """
        session_key = f'alb_logged_{user.usr_sf_id}'
        
        # Check if already logged in this session
        if request.session.get(session_key):
            return
        
        try:
            # Get client IP address
            ip_address = self._get_client_ip(request)
            
            # Get user agent
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
            
            # Create login log entry
            UserLoginLog.objects.create(
                ull_user_sf_id=user,
                ull_ip_address=ip_address,
                ull_user_agent=user_agent,
                ull_login_at=now()
            )
            
            # Mark as logged in this session
            request.session[session_key] = True
            
            logger.info(
                f"Login logged for user: {user.usr_email}, "
                f"IP: {ip_address}, UA: {user_agent[:50]}"
            )
            
        except Exception as e:
            logger.error(f"Error logging user login: {str(e)}")
    
    def _get_client_ip(self, request: HttpRequest) -> Optional[str]:
        """
        Extract client IP address from request.
        Handles X-Forwarded-For header for proxied requests.
        
        Args:
            request: Django HTTP request
            
        Returns:
            Client IP address or None
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Get first IP in chain (original client)
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        return ip
    
    def _render_error_response(self, message: str, error_code: str, status_code: int) -> HttpResponse:
        """
        Render an error response as HttpResponse for middleware.
        
        Args:
            message: Error message
            error_code: Error code
            status_code: HTTP status code
            
        Returns:
            HttpResponse with JSON error content
        """
        response_data = {
            "success": False,
            "message": message,
            "error_code": error_code
        }
        
        response = HttpResponse(
            json.dumps(response_data),
            content_type='application/json',
            status=status_code
        )
        return response
