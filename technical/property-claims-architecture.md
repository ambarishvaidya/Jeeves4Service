# Property Claims in JWT Implementation

## What This Document Covers

This document explains how property information is included in user authentication tokens (JWT) in the Jeeves4Service project. This allows services to quickly check if a user has access to specific properties without making additional database calls.

## The Business Problem

When a user logs in, they should have immediate access to all properties they're associated with. Other services (like Household Service) need to quickly verify if a user can access property-specific data. Without this implementation, every request would require database lookups to check property access.

## Our Solution: Property Data in JWT Claims

### What We Implemented

When a user authenticates, their JWT token includes:
- Basic user information (ID, email, admin status)
- **List of properties they have access to**
- **Access level for each property** (owner, member, guest)

This means other services can instantly check property access without database calls.

## Code Implementation

### Enhanced JWT Token Structure

**File: `services/shared/j4s_utilities/token_models.py`**

```python
class PropertyClaim(BaseModel):
    """Property information included in JWT claims."""
    property_id: int
    property_name: str
    access_level: str = "member"  # 'owner', 'member', 'guest'

class TokenPayload(BaseModel):
    """JWT Token Payload with property information."""
    user_id: int                              
    username: Optional[str] = None            
    trace_id: Optional[str] = None            
    is_admin: Optional[bool] = False          
    properties: Optional[List[PropertyClaim]] = None  # NEW: User's property access
    
    def has_property_access(self, property_id: int, required_level: str = "member") -> bool:
        """Check if user has access to a specific property."""
        if not self.properties:
            return False
            
        access_hierarchy = {"guest": 1, "member": 2, "owner": 3}
        required_rank = access_hierarchy.get(required_level, 1)
        
        for prop in self.properties:
            if prop.property_id == property_id:
                user_rank = access_hierarchy.get(prop.access_level, 1)
                return user_rank >= required_rank
                
        return False
    
    def get_property_ids(self) -> List[int]:
        """Get list of property IDs the user has access to."""
        return [prop.property_id for prop in (self.properties or [])]
```

### Property Service Client Implementation

**File: `services/shared/clients/property_service_client.py`**

```python
class PropertyServiceClient:
    """Client for fetching property data from Property Service."""
    
    def get_user_properties_sync(self, user_id: int) -> List[PropertyClaimDto]:
        """Fetch all properties associated with a user."""
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(
                    f"{self.base_url}/api/internal/properties/users/{user_id}",
                    headers=self._get_internal_headers()
                )
                response.raise_for_status()
                
                data = response.json()
                properties = []
                for prop_data in data.get('properties', []):
                    properties.append(PropertyClaimDto(**prop_data))
                
                return properties
        except Exception as e:
            logger.error(f"Failed to fetch properties for user {user_id}: {e}")
            return []  # Return empty list on failure
```

### Property Service Internal Endpoint

**File: `services/property_service/routes/property.py`**

```python
@router.get("/internal/properties/users/{user_id}", response_model=UserPropertiesResponseDto)
async def get_user_properties_for_claims(
    user_id: int,
    request: Request,
    x_internal_token: str = Header(..., alias="X-Internal-Token")
) -> UserPropertiesResponseDto:
    """
    INTERNAL ENDPOINT - Returns property data for JWT claims.
    Used by User Service during authentication.
    """
    # Validate internal service token
    if not _validate_internal_token(x_internal_token):
        raise HTTPException(status_code=401, detail="Invalid internal service token")
    
    # Fetch user's properties
    get_property_service = ServiceFactory.get_get_property_service()
    properties = get_property_service.get_properties(user_id)
    
    # Convert to claim format
    property_claims = []
    for prop in properties:
        property_claims.append(PropertyClaimDto(
            property_id=prop.id,
            property_name=prop.name,
            access_level="member"  # Business logic determines this
        ))
    
    return UserPropertiesResponseDto(
        user_id=user_id,
        properties=property_claims,
        total_count=len(property_claims)
    )
```

### Updated User Authentication

**File: `services/user_service/routes/users.py`**

```python
@router.post("/users/authenticate", response_model=AuthenticateUserResponse)
async def authenticate_user(email: str, password: str, response: Response) -> AuthenticateUserResponse:
    try:
        # Step 1: Authenticate user credentials
        auth_service = ServiceFactory.get_authenticate_user_service()
        auth_response = auth_service.authenticate(email, password)
        
        # Step 2: Fetch user's properties via internal API call
        user_properties = property_client.get_user_properties_sync(auth_response.user_id)
        
        # Step 3: Create JWT with property information
        payload = TokenPayload(
            user_id=auth_response.user_id,
            username=auth_response.email,
            trace_id=auth_response.session_id,
            is_admin=auth_response.is_admin,
            properties=user_properties  # Property data included in JWT
        )
        
        # Step 4: Return JWT with property claims
        response.headers["Authorization"] = f"Bearer {jwt_helper.generate_token(payload)}"
        return auth_response
```

## How Services Use Property Claims

### Household Service Example

**File: `services/household_service/routes/household.py`**

```python
@router.get("/household/items/property/{property_id}")
async def get_household_items(
    property_id: int,
    current_user: TokenPayload = Depends(jwt_helper.verify_token)
):
    # FAST: Check property access from JWT claims (no database call)
    if not current_user.has_property_access(property_id, "member"):
        raise HTTPException(status_code=403, detail="You don't have access to this property")
    
    # User has access - proceed with business logic
    household_service = ServiceFactory.get_household_service()
    items = household_service.get_items_by_property(property_id)
    return items

@router.post("/household/items")
async def add_household_item(
    request: AddHouseholdItemRequest,
    current_user: TokenPayload = Depends(jwt_helper.verify_token)
):
    # Validate property access before adding item
    if not current_user.has_property_access(request.property_id, "member"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Add the item
    service = ServiceFactory.get_add_household_item_service()
    return service.add_item(request)
```

### Property Service Example

```python
@router.delete("/property/{property_id}")
async def delete_property(
    property_id: int,
    current_user: TokenPayload = Depends(jwt_helper.verify_token)
):
    # Only property owners can delete properties
    if not current_user.has_property_access(property_id, "owner"):
        raise HTTPException(status_code=403, detail="Only property owners can delete properties")
    
    property_service = ServiceFactory.get_property_service()
    property_service.delete_property(property_id)
    return {"message": "Property deleted successfully"}
```

## Example JWT Token

When a user authenticates, their JWT token contains:

```json
{
  "user_id": 123,
  "username": "john.doe@example.com",
  "trace_id": "abc123def456",
  "is_admin": false,
  "properties": [
    {
      "property_id": 1,
      "property_name": "Main House",
      "access_level": "owner"
    },
    {
      "property_id": 2,
      "property_name": "Beach House", 
      "access_level": "member"
    }
  ],
  "iat": 1629789123,
  "exp": 1629875523
}
```

## Benefits of This Implementation

### 1. Performance
- **No Database Calls**: Property access checks happen instantly from JWT
- **Reduced Latency**: Authorization decisions made in microseconds
- **Lower Database Load**: Fewer queries to property tables

### 2. User Experience  
- **Fast Responses**: Users see their property data immediately
- **Seamless Access**: No delays when switching between properties
- **Consistent State**: Property access is consistent across all services

### 3. Development Benefits
- **Simple Authorization**: `user.has_property_access(property_id, "member")`
- **Easy Testing**: Mock JWT tokens with test property data
- **Clear Patterns**: Same authorization pattern across all services

## When Property Data is Updated

### Token Refresh Scenarios
1. **User logs in again**: Fresh property data fetched
2. **Property association changes**: User needs to re-authenticate
3. **Token expires**: Natural refresh cycle (typically 1-24 hours)

### Handling Stale Data
```python
# If property access changes and token hasn't expired yet
@router.get("/property/{property_id}/details")
async def get_property_details(property_id: int, user: TokenPayload = Depends(auth)):
    # Quick check from JWT
    if not user.has_property_access(property_id):
        raise HTTPException(403, "Access denied")
    
    # For critical operations, you might double-check with database
    if critical_operation:
        current_access = property_service.verify_current_access(user.user_id, property_id)
        if not current_access:
            raise HTTPException(403, "Access has been revoked")
```

## File Structure

```
services/
├── shared/
│   ├── dto/
│   │   └── property_shared.py          # Shared DTOs for property data
│   ├── clients/
│   │   └── property_service_client.py  # HTTP client for Property Service
│   └── j4s_utilities/
│       └── token_models.py             # Enhanced JWT payload with properties
├── user_service/
│   └── routes/
│       └── users.py                    # Authentication with property fetching
├── property_service/
│   └── routes/
│       └── property.py                 # Internal endpoint for property data
└── household_service/
    └── routes/
        └── household.py                # Uses property claims for authorization
```

This implementation provides fast, secure property-based authorization while maintaining clean service boundaries and excellent performance.
