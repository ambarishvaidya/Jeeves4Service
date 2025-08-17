# Internal Service Security Implementation

## Overview

This document explains how internal service communication is secured in the Jeeves4Service project. The system ensures that certain API endpoints are only accessible by internal services, not external users.

## The Problem We Solved

When the User Service needs to fetch property information during user authentication, it must call the Property Service. However, we don't want external users to be able to access this same endpoint directly, as it could expose sensitive data or be misused.

## Our Solution: Internal-Only Endpoints

### What We Implemented

**1. Separate Internal Routes**
- Regular user endpoints: `/api/properties/` 
- Internal service endpoints: `/api/internal/properties/users/{user_id}`

**2. Authentication Token Required**
- Internal endpoints require a special `X-Internal-Token` header
- Token is shared only between our services
- Invalid tokens are rejected with 401 error

**3. Request Logging**
- All internal service calls are logged for security monitoring
- Failed authentication attempts are logged with IP addresses

## Code Implementation Details

### Property Service (services/property_service/routes/property.py)

```python
# Internal service authentication
INTERNAL_SERVICE_TOKEN = os.getenv("INTERNAL_SERVICE_TOKEN", "your-secure-internal-token-here")

def _validate_internal_token(token: str) -> bool:
    """Validate internal service authentication token."""
    return token == INTERNAL_SERVICE_TOKEN

@router.get("/internal/properties/users/{user_id}", response_model=UserPropertiesResponseDto)
async def get_user_properties_for_claims(
    user_id: int,
    request: Request,
    x_internal_token: str = Header(..., alias="X-Internal-Token")
) -> UserPropertiesResponseDto:
    """
    INTERNAL ENDPOINT - NOT FOR PUBLIC ACCESS
    This endpoint is used by other services to fetch property data.
    """
    # Validate internal service token
    if not _validate_internal_token(x_internal_token):
        logger.warning(f"Invalid internal token access attempt from {request.client.host}")
        raise HTTPException(status_code=401, detail="Invalid internal service token")
    
    # Log internal access for audit trail
    _log_internal_access(user_id, request.client.host)
    
    # Fetch and return property data
    get_property_service = ServiceFactory.get_get_property_service()
    properties = get_property_service.get_properties(user_id)
    # ... rest of implementation
```

### Property Service Client (services/shared/clients/property_service_client.py)

```python
class PropertyServiceClient:
    def __init__(self, property_service_url: str = "http://localhost:8002"):
        self.base_url = property_service_url.rstrip('/')
        self.internal_token = os.getenv("INTERNAL_SERVICE_TOKEN", "your-secure-internal-token-here")
    
    def _get_internal_headers(self) -> dict:
        """Get headers for internal service authentication."""
        return {
            "Content-Type": "application/json",
            "X-Internal-Token": self.internal_token
        }
    
    def get_user_properties_sync(self, user_id: int) -> List[PropertyClaimDto]:
        """Fetch properties for a user using internal endpoint."""
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(
                    f"{self.base_url}/api/internal/properties/users/{user_id}",
                    headers=self._get_internal_headers()
                )
                response.raise_for_status()
                # ... process response
```

### User Service Integration (services/user_service/routes/users.py)

```python
from services.shared.clients.property_service_client import property_client

@router.post("/users/authenticate", response_model=AuthenticateUserResponse)
async def authenticate_user(email: str, password: str, response: Response) -> AuthenticateUserResponse:
    try:
        # Authenticate user first
        auth_service = ServiceFactory.get_authenticate_user_service()
        auth_response = auth_service.authenticate(email, password)
        
        # Fetch user's properties using internal service call
        user_properties = property_client.get_user_properties_sync(auth_response.user_id)
        
        # Create JWT token with property information
        payload = TokenPayload(
            user_id=auth_response.user_id,
            username=auth_response.email,
            trace_id=auth_response.session_id,
            is_admin=auth_response.is_admin,
            properties=user_properties  # Property data from internal call
        )
        
        response.headers["Authorization"] = f"Bearer {jwt_helper.generate_token(payload)}"
        return auth_response
```

## Environment Configuration

### .env.example
```bash
# Internal Service Authentication Configuration
INTERNAL_SERVICE_TOKEN=your-secure-internal-token-here-change-in-production
PROPERTY_SERVICE_URL=http://localhost:8002
```

## How It Works

### 1. User Authentication Flow
1. User logs in via User Service (`/users/authenticate`)
2. User Service validates credentials
3. User Service calls Property Service internal endpoint with token
4. Property Service validates internal token and returns property data
5. User Service includes property data in JWT claims
6. JWT token returned to user

### 2. Security Validation
- **External users cannot access** `/api/internal/properties/users/{user_id}` 
- **Only services with valid token** can access internal endpoints
- **All access attempts are logged** for security monitoring

### 3. Error Handling
```python
# Invalid token attempt
if not _validate_internal_token(x_internal_token):
    logger.warning(f"Invalid internal token access attempt from {request.client.host}")
    raise HTTPException(status_code=401, detail="Invalid internal service token")

# Service unavailable fallback
try:
    user_properties = property_client.get_user_properties_sync(user_id)
except Exception as e:
    logger.warning(f"Failed to fetch properties for user {user_id}: {e}")
    user_properties = []  # Continue without properties rather than fail
```

## Security Benefits

**1. Access Control**
- Internal endpoints are protected from external access
- Only authorized services can fetch sensitive data

**2. Audit Trail**
- All internal service calls are logged
- Failed authentication attempts are tracked

**3. Graceful Degradation**
- If Property Service is unavailable, authentication still works
- User gets JWT token without property claims

**4. Simple Implementation**
- Uses standard HTTP headers for authentication
- Easy to understand and maintain
- No complex service mesh required

## What's Protected

### Public Endpoints (External Users Can Access)
- `POST /api/users/authenticate` - User login
- `GET /api/properties/` - User's own properties (with JWT)
- `GET /api/property/{id}` - Specific property (with authorization check)

### Internal Endpoints (Services Only)
- `GET /api/internal/properties/users/{user_id}` - Requires internal token
- Future internal endpoints follow same pattern

This implementation ensures that sensitive cross-service communication is protected while maintaining the simplicity and clarity of your microservices architecture.
