# VS Code Test Discovery Configuration for Python Monorepo

## Overview
This document outlines the configuration and setup required for VS Code to properly discover and run tests in a Python monorepo structure with multiple services.

## Problem Statement
VS Code was unable to discover and run tests from multiple services in a Python monorepo structure. Tests were visible for some services (property_service, crypto tests) but not others (user_service), leading to inconsistent test discovery.

---

## Root Cause Analysis

### Primary Issues Identified:

#### 1. SQLAlchemy Table Redefinition Conflicts
- **Root Cause**: Multiple imports of SQLAlchemy models during test discovery caused "Table already defined" errors
- **Error Message**: `sqlalchemy.exc.InvalidRequestError: Table 'property.storage' is already defined for this MetaData instance`
- **Impact**: Prevented test collection from completing

#### 2. Inconsistent Import Patterns
- **Root Cause**: Mix of relative imports (`from app.services...`) and absolute imports (`from services.service_name.app...`) 
- **Error Message**: `ModuleNotFoundError: No module named 'app'` when pytest runs from workspace root
- **Impact**: Import failures when running tests from workspace root vs individual service directories

#### 3. Test Directory Structure Inconsistencies
- **Root Cause**: User service tests were nested in `tests/test_user_service/` while property service tests were flat in `tests/`
- **Error Message**: `ModuleNotFoundError: No module named 'tests.test_user_service'`
- **Impact**: Python treating nested test directories as packages, causing import conflicts

#### 4. Python Path Resolution Issues
- **Root Cause**: VS Code's pytest configuration wasn't properly configured for monorepo structure
- **Impact**: Import errors when running from workspace root vs individual service directories

---

## Solutions Implemented

### 1. Fixed SQLAlchemy Model Definitions

**What was done:**
- Added `'extend_existing': True` to all `__table_args__` in SQLAlchemy models
- Updated all model imports to use absolute paths

**Code Changes:**
```python
# Before
class Storage(Base):
    __tablename__ = "storage"
    __table_args__ = {'schema': "property"}

# After  
class Storage(Base):
    __tablename__ = "storage"
    __table_args__ = {'schema': "property", 'extend_existing': True}
```

**Files Modified:**
- `services/property_service/app/models/storage.py`
- `services/property_service/app/models/property.py` (Property, PropertyRooms, PropertyAssociation classes)
- `services/user_service/app/models/user.py` (User, UserPassword classes)

### 2. Standardized Import Patterns

**What was done:**
- Converted all relative imports to absolute imports across the entire codebase
- Updated both service files and model files to use full module paths

**Pattern Applied:**
```python
# Before (relative imports)
from app.dto.storage import PropertyStorageRequest
from app.models.storage import Storage
from app.db.base import Base

# After (absolute imports)  
from services.property_service.app.dto.storage import PropertyStorageRequest
from services.property_service.app.models.storage import Storage
from services.property_service.app.db.base import Base
```

**Files Modified:**
- All service files in `services/property_service/app/services/`:
  - `add_main_storage.py`
  - `add_property.py`
  - `add_rooms.py`
  - `add_storage.py`
  - `add_users_property.py`
  - `update_property.py`
  - `update_room.py`
- All model files in both services
- Database session files: `services/*/app/db/session.py`

### 3. Normalized Test Directory Structure

**What was done:**
- Moved user service tests from nested `tests/test_user_service/` to flat `tests/` structure
- Updated test imports to use absolute paths
- Removed `__init__.py` files from test directories to prevent package import conflicts

**Structure Change:**
```
# Before
services/user_service/tests/test_user_service/
├── test_authenticate_user.py
├── test_invite_user.py  
├── test_register_user.py
└── test_update_user.py

# After
services/user_service/tests/
├── test_authenticate_user.py
├── test_invite_user.py
├── test_register_user.py
└── test_update_user.py
```

**Import Updates in Test Files:**
```python
# Before
from app.services.authenticate_user import AuthenticateUser

# After
from services.user_service.app.services.authenticate_user import AuthenticateUser
```

### 4. Updated VS Code Configuration

**What was done:**
- Added workspace folder to Python analysis paths
- Configured pytest arguments for monorepo structure
- Set proper root directory and ignore patterns

**Final `.vscode/settings.json`:**
```json
{
  "python.analysis.extraPaths": [
    "${workspaceFolder}",
    "${workspaceFolder}/services/shared",
    "${workspaceFolder}/services/shared/j4s_logging_lib"
  ],
  "python.analysis.indexing": true,
  "python.analysis.autoImportCompletions": true,
  "python.analysis.exclude": [
    "**/__pycache__/**",
    "**/.venv/**",
    "**/.git/**",
    "**/*.egg-info/**"
  ],
  "python.analysis.diagnosticMode": "workspace",
  "python.testing.pytestArgs": [
    "--rootdir=${workspaceFolder}",
    "--ignore=services/property_service/app",
    "--ignore=services/user_service/app", 
    "services/property_service/tests",
    "services/user_service/tests",
    "services/tests"
  ],
  "python.testing.unittestEnabled": false,
  "python.testing.pytestEnabled": true
}
```

---

## Results Achieved

- ✅ **119 total tests discovered** (65 property + 51 user + 3 crypto)
- ✅ **Consistent test discovery** across all services
- ✅ **No SQLAlchemy conflicts** during test collection
- ✅ **Clean import resolution** from workspace root
- ✅ **VS Code test explorer** shows all tests from all services

---

## Guidelines for Adding New Services

### 1. Directory Structure Template

```
services/new_service/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── session.py
│   ├── dto/
│   │   ├── __init__.py
│   │   └── your_dto.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── your_model.py
│   └── services/
│       ├── __init__.py
│       └── your_service.py
├── tests/           # FLAT structure, NO subdirectories
│   ├── test_your_service.py
│   └── test_your_model.py
│   # NO __init__.py file in tests directory
├── alembic/
├── alembic.ini
├── main.py
└── pyproject.toml
```

### 2. Import Pattern Rules

**ALWAYS use absolute imports in all files:**

```python
# ✅ Correct - Service files
from services.new_service.app.dto.your_dto import YourRequest
from services.new_service.app.models.your_model import YourModel
from services.new_service.app.db.base import Base

# ✅ Correct - Test files  
from services.new_service.app.services.your_service import YourService
from services.new_service.app.models.your_model import YourModel

# ❌ Wrong - Never use relative imports
from app.dto.your_dto import YourRequest
from app.models.your_model import YourModel
```

### 3. SQLAlchemy Model Requirements

**Always include `extend_existing=True` in table args:**

```python
from services.new_service.app.db.base import Base

class YourModel(Base):
    __tablename__ = "your_table"
    __table_args__ = {"schema": "your_schema", "extend_existing": True}
    
    id = Column(Integer, primary_key=True, index=True)
    # ... other columns
```

### 4. VS Code Settings Update

**When adding a new service, update `.vscode/settings.json`:**

```json
{
  "python.testing.pytestArgs": [
    "--rootdir=${workspaceFolder}",
    "--ignore=services/property_service/app",
    "--ignore=services/user_service/app",
    "--ignore=services/new_service/app",     // Add this line
    "services/property_service/tests",
    "services/user_service/tests",
    "services/new_service/tests",            // Add this line
    "services/tests"
  ]
}
```

### 5. Test Directory Rules

- ✅ **DO**: Place test files directly in `services/new_service/tests/`
- ✅ **DO**: Use absolute imports in test files
- ✅ **DO**: Remove any `__init__.py` from test directories
- ✅ **DO**: Use descriptive test file names like `test_your_service.py`

- ❌ **DON'T**: Create nested test subdirectories like `tests/test_new_service/`
- ❌ **DON'T**: Use relative imports in test files
- ❌ **DON'T**: Add `__init__.py` files to test directories

### 6. Validation Checklist

Before considering a new service complete, verify:

1. **Test discovery**: 
   ```bash
   pytest --collect-only --rootdir=. services/new_service/tests
   ```

2. **Import validation**: 
   ```bash
   python -c "from services.new_service.app.services.your_service import YourService"
   ```

3. **SQLAlchemy check**: 
   ```bash
   python -c "from services.new_service.app.models.your_model import YourModel"
   ```

4. **VS Code integration**: Confirm tests appear in VS Code test explorer after restart

5. **Full workspace test collection**:
   ```bash
   pytest --collect-only --rootdir=. services/property_service/tests services/user_service/tests services/new_service/tests services/tests
   ```

---

## Troubleshooting Common Issues

### Issue: `ModuleNotFoundError: No module named 'app'`
**Solution**: Check that all imports use absolute paths (`services.service_name.app...`) instead of relative paths (`app...`)

### Issue: `Table 'schema.table_name' is already defined`
**Solution**: Add `'extend_existing': True` to the `__table_args__` in your SQLAlchemy model

### Issue: Tests not appearing in VS Code
**Solutions**:
1. Restart VS Code
2. Check that test files are in flat structure under `tests/`
3. Verify no `__init__.py` in test directories
4. Update `.vscode/settings.json` with new service paths

### Issue: Import errors in test files
**Solution**: Ensure test files use absolute imports to the service modules

---

## Notes for Future Developers

1. **Consistency is key**: Always follow the absolute import pattern across the entire codebase
2. **Test structure matters**: Keep test directories flat to avoid Python package conflicts
3. **SQLAlchemy considerations**: The `extend_existing=True` flag is crucial for test discovery in monorepos
4. **VS Code configuration**: Update settings.json whenever new services are added
5. **Validation is important**: Always run the validation checklist before considering a service complete

By following these guidelines, new services will integrate seamlessly with the existing test discovery infrastructure without requiring additional debugging or configuration changes.

---

## Configuration Reference

### Current Working Monorepo Structure
```
Jeeves4Service/
├── .vscode/
│   └── settings.json
├── services/
│   ├── property_service/
│   │   ├── app/
│   │   └── tests/               # 65 tests
│   ├── user_service/
│   │   ├── app/
│   │   └── tests/               # 51 tests
│   ├── shared/
│   │   ├── j4s_crypto_lib/
│   │   └── j4s_logging_lib/
│   └── tests/
│       └── test_j4s_crypto/     # 3 tests
├── requirements.txt
└── README.md
```

### Test Discovery Status
- **Total Tests**: 119
- **Property Service**: 65 tests ✅
- **User Service**: 51 tests ✅
- **Crypto Service**: 3 tests ✅
- **All services discoverable in VS Code Test Explorer**: ✅

---

*Document created: August 3, 2025*  
*Last updated: August 3, 2025*  
*Repository: Jeeves4Service*  
*Branch: feature/009-Converting-to-monorepo!*
