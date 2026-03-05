# ALB Authentication Documentation

## Overview

This document describes the AWS Application Load Balancer (ALB) OIDC authentication system integrated into the Agent360 backend. The system validates JWT tokens issued by AWS ALB and automatically resolves authenticated users from the database.

**Status**: ALB authentication is controlled by the `ALB_AUTH_ENABLED` environment variable. When disabled (default for local development), the system bypasses all authentication checks.

---

## Architecture

### Components

1. **ALB Auth Middleware** (`core/middleware/alb_auth_middleware.py`)
   - Intercepts all incoming requests
   - Validates JWT tokens from ALB
   - Resolves users from the database
   - Logs user login events

2. **JWT Verifier Service** (`core/services/alb_jwt_verifier.py`)
   - Verifies JWT signatures using ES256 algorithm
   - Fetches public keys from AWS ALB endpoint
   - Implements LRU caching for performance
   - Extracts user claims from verified tokens

3. **ALB Settings** (`core/config/alb_settings.py`)
   - Centralized configuration management
   - Loads environment variables with defaults
   - Provides typed access to ALB settings

4. **Auth Views** (`apps/users/auth_views.py`)
   - Logout endpoint for clearing ALB session cookies
   - Health check endpoint (no authentication required)

---

## Authentication Flow

```
Client Request
    ↓
ALB adds x-amzn-oidc-data header (JWT token)
    ↓
ALBAuthMiddleware.process_request()
    ↓
Check if ALB_AUTH_ENABLED
    ├─ false → Skip authentication (local dev)
    └─ true → Continue
    ↓
Check if path is exempt
    ├─ yes → Skip authentication
    └─ no → Continue
    ↓
Extract JWT from x-amzn-oidc-data header
    ├─ missing → Return 401 MISSING_AUTH_TOKEN
    └─ present → Continue
    ↓
ALBJWTVerifier.verify_token()
    ├─ Decode JWT header to get kid (key ID)
    ├─ Fetch public key from AWS (with caching)
    ├─ Verify signature using ES256
    ├─ Verify expiration
    ├─ invalid → Return 401 INVALID_AUTH_TOKEN
    └─ valid → Return claims
    ↓
Extract user info from claims
    ├─ missing email → Return 401 MISSING_EMAIL_CLAIM
    └─ email present → Continue
    ↓
Resolve user from database
    ├─ Try by email (usr_email)
    ├─ Fallback to federation ID (usr_federation_id)
    ├─ Check usr_is_active and usr_active flags
    ├─ not found/inactive → Return 403 USER_NOT_FOUND
    └─ found → Continue
    ↓
Attach user and claims to request
    ├─ request.user = user
    └─ request.alb_claims = claims
    ↓
Log first login of session
    ├─ Create UserLoginLog entry
    ├─ Record IP address and user agent
    └─ Mark session as logged
    ↓
Request proceeds to view
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ALB_AUTH_ENABLED` | `false` | Enable/disable ALB authentication |
| `AWS_REGION` | `us-east-1` | AWS region for ALB public key endpoint |
| `ALB_KEY_CACHE_TTL` | `3600` | Public key cache TTL in seconds (1 hour) |
| `ALB_KEY_CACHE_MAX_SIZE` | `100` | Maximum number of cached public keys |

### Example .env Configuration

```bash
# Enable ALB authentication in production
ALB_AUTH_ENABLED=true

# Set AWS region where ALB is deployed
AWS_REGION=us-east-1

# Cache settings (optional, uses defaults if not set)
ALB_KEY_CACHE_TTL=3600
ALB_KEY_CACHE_MAX_SIZE=100
```

---

## JWT Token Structure

### Header
```json
{
  "alg": "ES256",
  "kid": "key-id-from-alb",
  "typ": "JWT"
}
```

### Payload (Claims)
```json
{
  "sub": "federation-id",
  "email": "user@example.com",
  "given_name": "John",
  "family_name": "Doe",
  "iss": "https://auth.elb.region.amazonaws.com",
  "aud": "application-id",
  "exp": 1234567890,
  "iat": 1234567800
}
```

### Key Fields
- **sub**: Subject (federation ID) - unique identifier from identity provider
- **email**: User email address - used for database lookup
- **exp**: Expiration timestamp - validated by JWT verifier
- **iat**: Issued at timestamp

---

## Public Key Fetching

### URL Format
```
https://public-keys.auth.elb.{region}.amazonaws.com/{kid}
```

### Example
```
https://public-keys.auth.elb.us-east-1.amazonaws.com/abc123def456
```

### Caching Strategy

The JWT verifier implements an LRU (Least Recently Used) cache for public keys:

1. **Cache Hit**: If key is cached and TTL not expired, use cached key
2. **Cache Miss**: Fetch from AWS endpoint with 5-second timeout
3. **Cache Storage**: Store fetched key with timestamp
4. **Cache Eviction**: Remove oldest entry when cache reaches max size

**Benefits**:
- Reduces latency by avoiding repeated AWS API calls
- Handles key rotation gracefully (TTL-based expiration)
- Bounded memory usage (max size limit)

---

## Exempt Paths

The following paths do not require authentication:

| Path | Purpose |
|------|---------|
| `/api/health/` | Health check endpoint |
| `/admin/login/` | Django admin login |
| `/api/schema/` | API schema/documentation |
| `/api/docs/` | API documentation |

To add more exempt paths, modify `ALBAuthMiddleware.EXEMPT_PATHS`.

---

## Error Handling

### Authentication Errors

| Error Code | HTTP Status | Message | Cause |
|-----------|------------|---------|-------|
| `MISSING_AUTH_TOKEN` | 401 | Missing authentication token | No x-amzn-oidc-data header |
| `INVALID_AUTH_TOKEN` | 401 | Invalid authentication token | JWT verification failed |
| `MISSING_EMAIL_CLAIM` | 401 | Invalid token claims: missing email | Email not in JWT claims |
| `USER_NOT_FOUND` | 403 | User not found or inactive | User not in database or inactive |

### Error Response Format

```json
{
  "success": false,
  "message": "Invalid authentication token: Token has expired",
  "error_code": "INVALID_AUTH_TOKEN"
}
```

---

## User Resolution

### Database Lookup Strategy

1. **Primary Lookup**: Search by email (`usr_email`)
   - Fastest method, most common case
   - Requires email in JWT claims

2. **Fallback Lookup**: Search by federation ID (`usr_federation_id`)
   - Used if email lookup fails
   - Handles email changes in identity provider

3. **Validation Checks**:
   - `usr_is_active = True` (account not deleted)
   - `usr_active = 1` (account not suspended)

### User Model Fields

```python
class User(models.Model):
    usr_email = models.EmailField()
    usr_federation_id = models.CharField(max_length=255, null=True)
    usr_is_active = models.BooleanField(default=True)
    usr_active = models.IntegerField(default=1)
    usr_sf_id = models.CharField(max_length=255)
    # ... other fields
```

---

## Login Logging

### UserLoginLog Entry

When a user authenticates for the first time in a session, a login log entry is created:

```python
UserLoginLog.objects.create(
    ull_user_sf_id=user,
    ull_ip_address=ip_address,
    ull_user_agent=user_agent,
    ull_login_at=now()
)
```

### Session Tracking

- Session key: `alb_logged_{user.usr_sf_id}`
- Prevents duplicate login logs for same session
- Cleared when session expires

### IP Address Extraction

Handles proxied requests via `X-Forwarded-For` header:
```python
# X-Forwarded-For: client, proxy1, proxy2
# Extracts: client (first IP in chain)
```

---

## Logout

### Logout Endpoint

```
POST /api/auth/logout/
Authorization: Bearer {token}
```

### Response

```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

### Cookies Cleared

The logout endpoint clears ALB session cookies:
- `AWSELBAuthSessionCookie-0` through `AWSELBAuthSessionCookie-4`
- Sets `max_age=0` and `expires` to past date
- Clears Django session

### Cookie Attributes

```python
Set-Cookie: AWSELBAuthSessionCookie-0=; 
  Max-Age=0; 
  Expires=Thu, 01 Jan 1970 00:00:00 GMT; 
  Path=/; 
  Secure; 
  HttpOnly; 
  SameSite=None
```

---

## Health Check

### Endpoint

```
GET /api/health/
```

**No authentication required** - exempt path

### Response

```json
{
  "status": "healthy",
  "service": "agent360-backend",
  "timestamp": "2026-03-05T10:30:00Z"
}
```

---

## Request Object Enhancements

After successful authentication, the request object is enhanced with:

### request.user
- Django User instance
- Contains all user model fields
- Available in views and serializers

### request.alb_claims
- Dictionary of verified JWT claims
- Contains: email, sub, given_name, family_name, exp, iat, etc.
- Useful for accessing identity provider information

### Example Usage in Views

```python
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated

@api_view(['GET'])
def user_profile(request):
    user = request.user
    claims = request.alb_claims
    
    return Response({
        'email': user.usr_email,
        'name': f"{claims['given_name']} {claims['family_name']}",
        'federation_id': claims['sub']
    })
```

---

## Development Mode (ALB_AUTH_ENABLED=false)

When ALB authentication is disabled:

1. **Middleware Bypassed**: All authentication checks skipped
2. **request.user**: Not set by middleware (use Django's default)
3. **request.alb_claims**: Not set
4. **Use Case**: Local development without ALB setup

### Local Development Setup

```bash
# .env for local development
ALB_AUTH_ENABLED=false

# Run Django development server
python manage.py runserver
```

---

## Troubleshooting

### Issue: "Missing authentication token"

**Cause**: ALB not adding x-amzn-oidc-data header

**Solutions**:
1. Verify ALB OIDC configuration
2. Check ALB listener rules
3. Ensure request goes through ALB (not direct to backend)

### Issue: "Invalid token signature"

**Cause**: Public key mismatch or key rotation

**Solutions**:
1. Check AWS region matches ALB region
2. Verify ALB public key endpoint is accessible
3. Clear cache: `ALBJWTVerifier.clear_cache()`
4. Check JWT algorithm is ES256

### Issue: "Token has expired"

**Cause**: JWT exp claim is in the past

**Solutions**:
1. Check server time synchronization
2. Verify ALB token TTL settings
3. Check client clock is correct

### Issue: "User not found or inactive"

**Cause**: User not in database or account suspended

**Solutions**:
1. Verify user exists in database
2. Check `usr_is_active` and `usr_active` flags
3. Verify email in JWT matches database
4. Check federation ID if email lookup fails

### Issue: Slow Authentication

**Cause**: Public key fetching on every request

**Solutions**:
1. Verify cache is working: check logs for "Using cached public key"
2. Increase `ALB_KEY_CACHE_TTL` if keys rotate infrequently
3. Check AWS endpoint latency
4. Verify network connectivity to AWS

---

## Logging

### Log Levels

- **INFO**: Successful authentication, cache operations, login events
- **DEBUG**: Cache hits, path exemptions, token verification steps
- **WARNING**: Missing tokens, user not found, expired tokens
- **ERROR**: JWT verification failures, database errors, network errors

### Example Log Output

```
INFO: ALB Authentication is ENABLED
DEBUG: Verifying token with kid: abc123def456
DEBUG: Using cached public key for kid: abc123def456
INFO: Successfully verified token for user: user@example.com
DEBUG: User found by email: user@example.com
INFO: Login logged for user: user@example.com, IP: 192.168.1.1, UA: Mozilla/5.0...
```

### Enabling Debug Logging

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'core.middleware.alb_auth_middleware': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'core.services.alb_jwt_verifier': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

---

## Security Considerations

### Token Validation

- ✅ Signature verification using ES256 algorithm
- ✅ Expiration time validation
- ✅ Key ID (kid) validation
- ✅ Public key fetched from AWS (not hardcoded)

### Transport Security

- ✅ HTTPS required for ALB communication
- ✅ Secure cookies (HttpOnly, Secure, SameSite=None)
- ✅ X-Forwarded-For header trusted (ALB is trusted proxy)

### Session Security

- ✅ Session key includes user SF ID (prevents session fixation)
- ✅ Login logs track IP and user agent
- ✅ Logout clears all session cookies

### Best Practices

1. **Always use HTTPS** in production
2. **Rotate ALB keys regularly** (AWS handles this)
3. **Monitor login logs** for suspicious activity
4. **Keep cache TTL reasonable** (balance between performance and key rotation)
5. **Validate email in JWT** before database lookup
6. **Log all authentication failures** for security auditing

---

## Integration with Django REST Framework

### Permission Classes

```python
from rest_framework.permissions import IsAuthenticated

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_view(request):
    # request.user is set by ALB middleware
    return Response({'user': request.user.usr_email})
```

### Serializers

```python
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['usr_email', 'usr_sf_id', 'usr_is_active']
```

### Views

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        claims = request.alb_claims
        
        return Response({
            'email': user.usr_email,
            'federation_id': claims['sub'],
            'name': f"{claims['given_name']} {claims['family_name']}"
        })
```

---

## Testing

### Unit Tests

Located in `tests/auth/`:

- `test_alb_auth_middleware.py` - Middleware behavior
- `test_alb_jwt_verifier.py` - JWT verification
- `test_auth_views.py` - Auth endpoints

### Running Tests

```bash
# Run all auth tests
python manage.py test tests.auth

# Run specific test
python manage.py test tests.auth.test_alb_jwt_verifier

# Run with verbose output
python manage.py test tests.auth -v 2
```

### Mocking ALB Tokens

```python
import jwt
from datetime import datetime, timedelta

# Create test token
payload = {
    'sub': 'test-federation-id',
    'email': 'test@example.com',
    'given_name': 'Test',
    'family_name': 'User',
    'exp': datetime.utcnow() + timedelta(hours=1),
    'iat': datetime.utcnow()
}

token = jwt.encode(payload, 'secret', algorithm='HS256')
```

---

## Related Documentation

- [Users API](USERS_API.md) - User management endpoints
- [Code Standards](CODE_STANDARDS.md) - Development standards
- [Database Schema](DATABASE_SCHEMA.md) - User model schema
- [Development Workflow](DEVELOPMENT_WORKFLOW.md) - Setup and deployment

---

## Support

For issues or questions about ALB authentication:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review logs in `logs/django.log`
3. Verify environment variables in `.env`
4. Check AWS ALB configuration
5. Contact the development team
