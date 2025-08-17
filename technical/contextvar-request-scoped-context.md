# Request-Scoped Context Management Design

## Design Overview

This document outlines the design and implementation of request-scoped context management in Jeeves4Service using Python's ContextVar. The solution addresses the need to pass user authentication and request-specific data across service layers without polluting method signatures.

## Problem Statement

### Current Challenges
- Service methods require explicit authentication parameters
- User context must be passed through multiple layers of function calls
- Adding new context data requires updating numerous method signatures
- Difficult to implement cross-cutting concerns like audit logging and authorization

### Business Requirements
- Secure access control based on user's property memberships
- Audit trail showing which user performed each operation
- Clean service interfaces that focus on business logic
- Scalable architecture that supports future context data needs

## Design Goals

### Primary Objectives
1. **Clean Separation of Concerns**: Business logic separated from context management
2. **Security**: User context isolated per request with no data leakage
3. **Maintainability**: Adding new context data doesn't break existing interfaces
4. **Performance**: Minimal overhead for context access
5. **Testability**: Easy to mock and test context-dependent code

### Non-Goals
- Global state management across multiple requests
- Persistent storage of context data
- Complex context inheritance or merging

## Architecture Design

### Component Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Route Layer   │───▶│  Context Layer   │───▶│ Service Layer   │
│                 │    │                  │    │                 │
│ - JWT Validation│    │ - Token Storage  │    │ - Business Logic│
│ - Context Setup │    │ - Data Retrieval │    │ - Context Access│
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Key Components

#### 1. RequestContext (Context Layer)
**Purpose**: Centralized request-scoped data storage and retrieval

**Responsibilities**:
- Store TokenPayload objects per request
- Provide clean API for context access
- Ensure request isolation

**Interface**:
```python
class RequestContext:
    @staticmethod
    def set_token(payload: TokenPayload) -> None
    
    @staticmethod
    def get_token() -> Optional[TokenPayload]
```

#### 2. TokenPayload (Data Layer)
**Purpose**: Structured representation of user authentication and authorization data

**Responsibilities**:
- Validate token structure
- Provide helper methods for authorization checks
- Encapsulate user property access logic

#### 3. Service Integration (Business Layer)
**Purpose**: Access user context for business logic implementation

**Responsibilities**:
- Retrieve current user context
- Apply user-specific business rules
- Filter data based on user permissions

## Implementation Strategy

### Phase 1: Foundation
1. **Context Infrastructure**
   - Create RequestContext class with ContextVar backing
   - Implement basic set/get operations
   - Add type safety with proper annotations

2. **Route Integration**
   - Modify FastAPI dependencies to set context
   - Update route handlers to use TokenPayload objects
   - Ensure context is set before service calls

### Phase 2: Service Integration
1. **Service Updates**
   - Update services to access RequestContext
   - Implement user-based data filtering
   - Add authorization checks using context data

2. **Testing Framework**
   - Create mock utilities for context testing
   - Update existing tests to use context mocking
   - Add context-specific test scenarios

### Phase 3: Enhancement
1. **Additional Context Data**
   - Request ID for tracing
   - Feature flags
   - Tenant information (future)

2. **Monitoring & Logging**
   - Context-aware logging
   - Performance metrics
   - Security audit trails

## Data Flow Design

### Request Processing Flow

```
1. HTTP Request → FastAPI Router
                     ↓
2. JWT Dependency → Token Validation
                     ↓
3. Route Handler → RequestContext.set_token(token_payload)
                     ↓
4. Service Call → Service accesses RequestContext.get_token()
                     ↓
5. Business Logic → Uses token data for authorization/filtering
                     ↓
6. Response → Context automatically cleaned up
```

### Context Lifecycle

| Phase | Action | Responsibility |
|-------|--------|----------------|
| Request Start | Create isolated context | FastAPI/ContextVar |
| Authentication | Validate and parse JWT | JWT Helper |
| Context Setup | Store TokenPayload | Route Handler |
| Business Logic | Access context data | Service Layer |
| Request End | Context cleanup | FastAPI/ContextVar |

## Security Design

### Isolation Guarantees
- **Request Isolation**: Each HTTP request gets independent context
- **No Cross-Request Leakage**: ContextVar ensures automatic isolation
- **Memory Safety**: Context cleaned up automatically when request completes

### Authorization Pattern
```python
def find_household_items(self, search_term: str):
    current_user = RequestContext.get_token()
    if not current_user:
        raise UnauthorizedException("No user context")
    
    # Filter by user's accessible properties
    accessible_properties = current_user.get_property_ids()
    if not accessible_properties:
        return empty_result()
    
    # Apply property-based filtering to query
    query = query.where(Item.property_id.in_(accessible_properties))
```

## Error Handling Design

### Context Availability
- **Missing Context**: Service methods handle gracefully with appropriate errors
- **Invalid Context**: Type validation at context boundaries
- **Context Corruption**: Defensive programming with null checks

### Fallback Strategies
- **Anonymous Access**: Some operations may work without user context
- **Default Behavior**: Sensible defaults when context is unavailable
- **Error Propagation**: Clear error messages for context-related failures

## Testing Strategy

### Test Categories

#### 1. Unit Tests
- **Context Operations**: Set/get functionality
- **Service Logic**: Business logic with mocked context
- **Authorization**: User permission scenarios

#### 2. Integration Tests
- **End-to-End Flow**: Request → Context → Service → Response
- **Security Tests**: Cross-request isolation verification
- **Error Scenarios**: Missing or invalid context handling

### Mock Strategy
```python
# Test helper for context mocking
def create_mock_user_context(property_ids=None, user_id=123):
    mock_token = Mock()
    mock_token.user_id = user_id
    mock_token.get_property_ids.return_value = property_ids or [201]
    return mock_token

# Usage in tests
with patch('service.module.RequestContext.get_token', return_value=mock_token):
    result = service.find_items("search term")
    assert result is not None
```

## Performance Considerations

### Design Optimizations
- **ContextVar Efficiency**: O(1) lookup time for context access
- **Minimal Memory Overhead**: Context limited to essential user data
- **Automatic Cleanup**: No manual memory management required

### Scalability Factors
- **Stateless Design**: Each request independent, supports horizontal scaling
- **Context Size**: TokenPayload kept minimal to reduce memory usage
- **Caching Strategy**: Context data cached for request duration only

## Migration Plan

### Backward Compatibility
- **Existing APIs**: No breaking changes to public interfaces
- **Gradual Adoption**: Services can adopt context access incrementally
- **Fallback Support**: Legacy code continues to work during transition

### Implementation Steps
1. **Deploy Context Infrastructure**: RequestContext and supporting utilities
2. **Update Route Handlers**: Set context in authentication flow
3. **Migrate Services**: Update services one by one to use context
4. **Update Tests**: Modify test suites to use context mocking
5. **Documentation**: Update API docs and developer guidelines

## Monitoring and Observability

### Metrics to Track
- **Context Setup Rate**: Percentage of requests setting context successfully
- **Context Access Patterns**: Which services access context most frequently
- **Authorization Failures**: Context-related permission denials
- **Performance Impact**: Latency overhead of context operations

### Logging Strategy
- **Context Correlation**: Include user ID in all log entries
- **Security Events**: Log authorization decisions and context access
- **Error Tracking**: Monitor context-related error patterns

## Future Enhancements

### Phase 2 Features
- **Request Tracing**: Add request ID to context for distributed tracing
- **Feature Flags**: Context-aware feature toggles
- **Multi-Tenant Support**: Tenant isolation using context

### Potential Extensions
- **Context Middleware**: Automated context setup for common patterns
- **Context Validation**: Runtime validation of context data consistency
- **Context Metrics**: Built-in performance monitoring

## Technical Usage Guide

### Basic Implementation Patterns

#### Setting Up Context in Routes
```python
from fastapi import Depends
from services.shared.request_context import RequestContext
from services.shared.j4s_jwt_lib.jwt_helper import jwt_helper

@router.get("/household/find/{item}")
async def find_household_item(
    item: str, 
    current_user: TokenPayload = Depends(jwt_helper.verify_token)
):
    # Set context for this request
    RequestContext.set_token(current_user)
    
    # Call service - context is automatically available
    service = ServiceFactory.get_find_item_service()
    return service.find_household_item(item)
```

#### Accessing Context in Services
```python
from services.shared.request_context import RequestContext

class FindItemService:
    def find_household_item(self, search_term: str):
        # Access user context from anywhere in the call stack
        current_user = RequestContext.get_token()
        
        if not current_user:
            raise UnauthorizedException("No user context available")
        
        # Use token data for business logic
        accessible_properties = current_user.get_property_ids()
        if not accessible_properties:
            return []  # User has no accessible properties
        
        # Apply property-based filtering
        query = self.db.query(Household).filter(
            Household.name.ilike(f"%{search_term}%"),
            Household.property_id.in_(accessible_properties)
        )
        
        return query.all()
```

#### Error Handling Patterns
```python
class BaseService:
    def get_current_user_or_fail(self) -> TokenPayload:
        """Helper method for services that require user context."""
        current_user = RequestContext.get_token()
        if not current_user:
            raise UnauthorizedException("Authentication required")
        return current_user
    
    def get_current_user_safe(self) -> Optional[TokenPayload]:
        """Helper method for services that can work without user context."""
        return RequestContext.get_token()

class FindItemService(BaseService):
    def find_household_item(self, search_term: str):
        current_user = self.get_current_user_or_fail()
        # Rest of implementation...
```

### Testing Strategies

#### 1. Unit Test Mocking

**Basic Mock Setup**
```python
import pytest
from unittest.mock import Mock, patch
from services.household_service.app.services.find_item import FindItemService

class TestFindItemService:
    def setup_method(self):
        self.service = FindItemService()
    
    def create_mock_token(self, property_ids=None, user_id=123):
        """Helper to create mock token payload."""
        mock_token = Mock()
        mock_token.user_id = user_id
        mock_token.get_property_ids.return_value = property_ids or [201, 202]
        return mock_token
    
    @patch('services.household_service.app.services.find_item.RequestContext.get_token')
    def test_find_household_item_success(self, mock_get_token):
        # Arrange
        mock_token = self.create_mock_token(property_ids=[201, 202])
        mock_get_token.return_value = mock_token
        
        # Act
        result = self.service.find_household_item("laptop")
        
        # Assert
        assert result is not None
        mock_get_token.assert_called_once()
```

**Testing No Context Scenario**
```python
@patch('services.household_service.app.services.find_item.RequestContext.get_token')
def test_find_household_item_no_context(self, mock_get_token):
    # Arrange - No user context available
    mock_get_token.return_value = None
    
    # Act & Assert
    with pytest.raises(UnauthorizedException, match="No user context"):
        self.service.find_household_item("laptop")
```

**Testing Empty Property Access**
```python
@patch('services.household_service.app.services.find_item.RequestContext.get_token')
def test_find_household_item_no_accessible_properties(self, mock_get_token):
    # Arrange - User has no accessible properties
    mock_token = self.create_mock_token(property_ids=[])
    mock_get_token.return_value = mock_token
    
    # Act
    result = self.service.find_household_item("laptop")
    
    # Assert
    assert result == []  # Should return empty list
```

#### 2. Integration Test Patterns

**Full Request Context Testing**
```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

class TestHouseholdRoutes:
    @patch('services.shared.j4s_jwt_lib.jwt_helper.jwt_helper.verify_token')
    def test_find_household_item_integration(self, mock_verify_token, test_client):
        # Arrange
        mock_token = Mock()
        mock_token.user_id = 123
        mock_token.get_property_ids.return_value = [201, 202]
        mock_verify_token.return_value = mock_token
        
        # Act
        response = test_client.get(
            "/household/find/laptop",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == 200
        mock_verify_token.assert_called_once()
```

#### 3. Context Fixture Patterns

**Pytest Fixtures for Context**
```python
@pytest.fixture
def mock_user_context():
    """Fixture that provides a mock user context."""
    mock_token = Mock()
    mock_token.user_id = 123
    mock_token.username = "testuser"
    mock_token.get_property_ids.return_value = [201, 202]
    return mock_token

@pytest.fixture
def admin_user_context():
    """Fixture for admin user with extended property access."""
    mock_token = Mock()
    mock_token.user_id = 999
    mock_token.username = "admin"
    mock_token.get_property_ids.return_value = [201, 202, 203, 204, 205]
    mock_token.is_admin = True
    return mock_token

@pytest.fixture
def no_access_user_context():
    """Fixture for user with no property access."""
    mock_token = Mock()
    mock_token.user_id = 456
    mock_token.username = "limited_user"
    mock_token.get_property_ids.return_value = []
    return mock_token
```

**Using Context Fixtures**
```python
class TestFindItemService:
    @patch('services.household_service.app.services.find_item.RequestContext.get_token')
    def test_admin_can_access_all_properties(self, mock_get_token, admin_user_context):
        # Arrange
        mock_get_token.return_value = admin_user_context
        
        # Act
        result = self.service.find_household_item("laptop")
        
        # Assert
        # Verify query includes all admin properties
        assert len(result) > 0  # Admin should see more results
    
    @patch('services.household_service.app.services.find_item.RequestContext.get_token')
    def test_limited_user_sees_no_results(self, mock_get_token, no_access_user_context):
        # Arrange
        mock_get_token.return_value = no_access_user_context
        
        # Act
        result = self.service.find_household_item("laptop")
        
        # Assert
        assert result == []  # No property access = no results
```

### Common Testing Pitfalls

#### 1. Wrong Mock Patch Path
```python
# ❌ Wrong: Patching where RequestContext is defined
@patch('services.shared.request_context.RequestContext.get_token')

# ✅ Correct: Patching where RequestContext is imported/used
@patch('services.household_service.app.services.find_item.RequestContext.get_token')
```

#### 2. Incomplete Mock Objects
```python
# ❌ Wrong: Mock without required methods
mock_token = Mock()
mock_token.user_id = 123
# Missing get_property_ids method will cause AttributeError

# ✅ Correct: Mock with all required methods
mock_token = Mock()
mock_token.user_id = 123
mock_token.get_property_ids.return_value = [201, 202]
```

#### 3. Context Pollution Between Tests
```python
# ✅ Good: Each test gets fresh mock context
class TestFindItemService:
    def setup_method(self):
        # Reset any global state if needed
        pass
    
    @patch('services.household_service.app.services.find_item.RequestContext.get_token')
    def test_each_method(self, mock_get_token):
        # Fresh mock for each test
        mock_get_token.return_value = self.create_mock_token()
```

### Debugging Context Issues

#### 1. Context Not Available
```python
def debug_context_availability(self):
    current_user = RequestContext.get_token()
    if current_user is None:
        # Check if context was set in route handler
        # Verify mock is patching correct import path
        # Ensure test is calling service through proper flow
        pass
```

#### 2. Mock Not Working
```python
def test_debug_mock_setup(self):
    with patch('your.service.module.RequestContext.get_token') as mock_get_token:
        mock_token = Mock()
        mock_token.get_property_ids.return_value = [201]
        mock_get_token.return_value = mock_token
        
        # Add debug prints to verify mock is called
        result = self.service.find_household_item("test")
        
        print(f"Mock called: {mock_get_token.called}")
        print(f"Mock call count: {mock_get_token.call_count}")
        print(f"Mock return value: {mock_get_token.return_value}")
```

### Best Practices for Context Testing

1. **Use Descriptive Test Names**: `test_find_item_with_admin_access` vs `test_find_item_1`

2. **Test All Context Scenarios**:
   - Valid user context
   - Missing context (None)
   - User with no property access
   - User with limited property access
   - Admin/super user access

3. **Verify Context Usage**:
   - Assert that context methods are called
   - Verify correct property IDs are used in queries
   - Test error handling for missing context

4. **Isolate Context Logic**:
   - Test context setup separately from business logic
   - Mock external dependencies (database, APIs)
   - Focus on context-specific behavior

5. **Use Fixtures for Common Scenarios**:
   - Standard user contexts
   - Edge case contexts (empty properties, admin)
   - Error conditions (invalid tokens)

## Conclusion

This design provides a scalable, secure foundation for request-scoped context management in Jeeves4Service. The solution maintains clean separation of concerns while enabling sophisticated authorization and audit capabilities. The phased implementation approach ensures minimal disruption to existing functionality while providing a clear path for future enhancements.

The technical usage patterns and testing strategies outlined above ensure that the context management system can be effectively implemented, tested, and maintained across the entire service architecture.
