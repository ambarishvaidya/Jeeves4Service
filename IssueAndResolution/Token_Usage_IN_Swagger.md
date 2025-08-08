# JWT Token Authentication in Swagger UI

## 📋 Overview

This document explains how JWT token authentication was implemented in our FastAPI application to enable easy token usage in Swagger UI documentation. The implementation provides a user-friendly way to authenticate API requests without manually adding Authorization headers.

## 🎯 Purpose and Goals

### Before Implementation
- Users had to manually add `Authorization: Bearer <token>` header for each protected endpoint
- No visual indication in Swagger UI about which endpoints require authentication
- Poor developer experience when testing protected APIs

### After Implementation
- **🔒 Authorize button** appears in Swagger UI
- One-click authentication for all protected endpoints
- Visual indicators (🔒 icons) on protected endpoints
- Automatic token inclusion in all authenticated requests

## 🔧 Technical Implementation

### Key Components Added

#### 1. FastAPI Security Imports
```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
```

#### 2. Security Scheme Instance
```python
security = HTTPBearer()
```

#### 3. Updated Token Verification Function
```python
def verify_token(authorization: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = authorization.credentials  # Clean token without "Bearer" prefix
    # Validation logic...
```

## 🧠 Understanding HTTPBearer and HTTPAuthorizationCredentials

### HTTPBearer Class

**Purpose**: Defines a security scheme for Bearer token authentication in FastAPI/OpenAPI

**What it does**:
- Automatically integrates with OpenAPI specification
- Creates the "Authorize" button in Swagger UI
- Validates that incoming requests have proper `Authorization: Bearer <token>` header format
- Extracts the token from the header automatically

**Key Benefits**:
```python
security = HTTPBearer()
# This single line:
# 1. Adds security scheme to OpenAPI spec
# 2. Creates Swagger UI authorization button
# 3. Validates header format automatically
# 4. Provides type safety for token extraction
```

### HTTPAuthorizationCredentials Class

**Purpose**: Container object that holds the extracted authorization credentials

**Structure**:
```python
class HTTPAuthorizationCredentials:
    scheme: str      # Always "Bearer" for HTTPBearer
    credentials: str # The actual token (without "Bearer" prefix)
```

**Usage**:
```python
def verify_token(auth: HTTPAuthorizationCredentials = Depends(security)):
    # auth.scheme = "Bearer"
    # auth.credentials = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    token = auth.credentials  # Clean token ready for validation
```

## 📝 Step-by-Step Implementation

### Step 1: Import Required Classes
```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends
```

### Step 2: Create Security Scheme
```python
# This creates the security scheme for OpenAPI
security = HTTPBearer()
```

### Step 3: Update Dependency Function
**Before** (Manual Header Parsing):
```python
def verify_token(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing auth header")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid format")
    
    token = authorization.replace("Bearer ", "", 1)  # Manual parsing
    # Validation logic...
```

**After** (Using HTTPBearer):
```python
def verify_token(authorization: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = authorization.credentials  # Automatic parsing, no "Bearer" prefix
    # Validation logic stays the same...
```

### Step 4: Apply to Protected Endpoints
```python
@router.post("/users/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: dict = Depends(verify_token)  # 🔒 icon appears in Swagger
):
    # Endpoint logic...
```

## 🎨 Swagger UI Changes

### Visual Indicators
- **🔒 Authorize Button**: Appears in top-right corner of Swagger UI
- **🔒 Lock Icons**: Appear next to protected endpoints
- **Authorization Modal**: Popup for entering Bearer token

### User Workflow
1. **Get Token**: Call `/users/authenticate` endpoint
2. **Copy Token**: From response header `Authorization: Bearer <token>`
3. **Authorize**: Click 🔒 button, paste token (with or without "Bearer" prefix)
4. **Test**: All protected endpoints now automatically include the token

## 🔍 Code Comparison

### Authentication Flow

#### Old Manual Approach
```python
# User has to manually add this header for each request:
headers = {"Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."}
```

#### New HTTPBearer Approach
```python
# User clicks 🔒 button once, enters token, all requests authenticated automatically
# FastAPI handles header injection transparently
```

### Token Extraction

#### Old Manual Parsing
```python
def verify_token(authorization: Optional[str] = Header(None)):
    # Manual validation and parsing
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(...)
    token = authorization.replace("Bearer ", "", 1)
```

#### New Automatic Parsing
```python
def verify_token(auth: HTTPAuthorizationCredentials = Depends(security)):
    # Automatic validation and parsing by FastAPI
    token = auth.credentials  # Clean token, ready to use
```

## 🚀 Benefits Achieved

### Developer Experience
- **One-click authentication** instead of manual header management
- **Visual feedback** about which endpoints require authentication
- **Consistent UX** across all protected endpoints

### Security
- **Standardized format** validation (HTTPBearer enforces proper format)
- **Type safety** with HTTPAuthorizationCredentials
- **Automatic error handling** for malformed headers

### Maintenance
- **Less boilerplate** code for token extraction
- **OpenAPI compliance** automatically maintained
- **Future-proof** for additional security schemes

## 🔧 Configuration Notes

### Security Scheme Customization
```python
# Basic usage
security = HTTPBearer()

# With custom description
security = HTTPBearer(
    scheme_name="JWT Bearer Token",
    description="Enter your JWT token obtained from /users/authenticate"
)
```

### FastAPI App Enhancement
```python
app = FastAPI(
    title="User Service API",
    description="""
    ## Authentication
    1. Call `/users/authenticate` to get your token
    2. Click the 🔒 Authorize button
    3. Enter your token (Bearer prefix optional)
    4. Test protected endpoints with automatic authentication
    """,
    # ... other config
)
```

## 🐛 Troubleshooting

### Common Issues

1. **No Authorize Button**: Ensure `HTTPBearer()` instance is created and used in `Depends()`
2. **Token Not Working**: Verify token format and validation logic
3. **401 Errors**: Check that token is properly decoded and validated

### Debugging Tips
```python
def verify_token(auth: HTTPAuthorizationCredentials = Depends(security)):
    print(f"Scheme: {auth.scheme}")        # Should be "Bearer"
    print(f"Token: {auth.credentials}")    # Your JWT token
    # Your validation logic...
```

## 📚 References

- [FastAPI Security Documentation](https://fastapi.tiangolo.com/tutorial/security/)
- [OpenAPI Security Schemes](https://swagger.io/docs/specification/authentication/)
- [JWT.io - JWT Token Debugger](https://jwt.io/)

## 📝 Related Files

- `services/user_service/routes/users.py` - Token verification implementation
- `services/user_service/main.py` - FastAPI app configuration
- `services/shared/j4s_jwt_lib/jwt_processor.py` - JWT token processing logic

---

**Author**: Development Team  
**Date**: August 8, 2025  
**Version**: 1.0  
**Status**: Implemented and Tested
