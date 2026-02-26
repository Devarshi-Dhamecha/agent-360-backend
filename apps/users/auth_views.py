"""
Authentication Views
Handles logout and health check endpoints.
"""
import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request: Request) -> Response:
    """
    Logout endpoint that clears ALB session cookie.
    
    POST /api/auth/logout/
    
    Returns:
        Response with Set-Cookie header to delete AWSELBAuthSessionCookie-0
    """
    logger.info(f"Logout requested by user: {getattr(request.user, 'usr_email', 'unknown')}")
    
    response = Response(
        {
            'success': True,
            'message': 'Logged out successfully'
        },
        status=200
    )
    
    # Delete ALB session cookie
    response.set_cookie(
        key='AWSELBAuthSessionCookie-0',
        value='',
        max_age=0,
        expires='Thu, 01 Jan 1970 00:00:00 GMT',
        path='/',
        secure=True,
        httponly=True,
        samesite='None'
    )
    
    # Also delete additional ALB cookies if they exist
    for i in range(5):  # ALB can use multiple cookie fragments
        response.set_cookie(
            key=f'AWSELBAuthSessionCookie-{i}',
            value='',
            max_age=0,
            expires='Thu, 01 Jan 1970 00:00:00 GMT',
            path='/',
            secure=True,
            httponly=True,
            samesite='None'
        )
    
    # Clear Django session
    if hasattr(request, 'session'):
        request.session.flush()
    
    logger.info("Logout completed, cookies cleared")
    return response


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request: Request) -> Response:
    """
    Health check endpoint - no authentication required.
    
    GET /api/health/
    
    Returns:
        200 OK with status information
    """
    return Response(
        {
            'status': 'healthy',
            'service': 'agent360-backend',
            'timestamp': request.META.get('HTTP_DATE', 'N/A')
        },
        status=200
    )
