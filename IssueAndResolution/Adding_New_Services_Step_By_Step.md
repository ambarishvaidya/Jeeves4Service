# Step-by-Step Guide: Adding New Services for Testing

## Overview
This document provides explicit, actionable steps for adding new services to the monorepo while ensuring proper test discovery and VS Code integration.

---

## Prerequisites
- Ensure you have read `Converting_To_Monorepo.md` for background context
- VS Code with Python extension installed
- Working virtual environment in the project root

---

## Step-by-Step Process

### Phase 1: Service Directory Setup

#### Step 1: Create Service Structure
```bash
# Navigate to services directory
cd services/

# Create new service directory
mkdir new_service_name

# Create the required subdirectories
mkdir new_service_name/app
mkdir new_service_name/app/db
mkdir new_service_name/app/dto
mkdir new_service_name/app/models
mkdir new_service_name/app/services
mkdir new_service_name/tests
mkdir new_service_name/alembic
mkdir new_service_name/alembic/versions
```

#### Step 2: Create Required Files
```bash
# Navigate to your new service
cd new_service_name/

# Create __init__.py files (DO NOT create in tests directory)
touch app/__init__.py
touch app/db/__init__.py
touch app/dto/__init__.py
touch app/models/__init__.py
touch app/services/__init__.py

# Create main configuration files
touch main.py
touch pyproject.toml
touch alembic.ini
```

### Phase 2: Database Setup

#### Step 3: Create Base Database Configuration
Create `app/db/base.py`:
```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```

#### Step 4: Create Database Session Configuration
Create `app/db/session.py`:
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from services.new_service_name.app.config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

#### Step 5: Create Configuration File
Create `app/config.py`:
```python
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")
```

### Phase 3: Model Creation

#### Step 6: Create SQLAlchemy Models
Create `app/models/your_model.py`:
```python
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import Mapped
from services.new_service_name.app.db.base import Base

class YourModel(Base):
    __tablename__ = "your_table"
    __table_args__ = {"schema": "your_schema", "extend_existing": True}
    
    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    name: Mapped[str] = Column(String(100), nullable=False)
    is_active: Mapped[bool] = Column(Boolean, default=True)
    # Add other fields as needed
```

**⚠️ CRITICAL**: Always include `"extend_existing": True` in `__table_args__`

### Phase 4: DTO Creation

#### Step 7: Create Data Transfer Objects
Create `app/dto/your_dto.py`:
```python
from pydantic import BaseModel
from typing import Optional

class YourRequest(BaseModel):
    name: str
    is_active: Optional[bool] = True

class YourResponse(BaseModel):
    id: int
    name: str
    is_active: bool
    message: str
```

### Phase 5: Service Implementation

#### Step 8: Create Business Logic Services
Create `app/services/your_service.py`:
```python
from services.new_service_name.app.models.your_model import YourModel
from services.new_service_name.app.dto.your_dto import YourRequest, YourResponse

class YourService:
    def __init__(self, logger, session):
        self.logger = logger
        self.session = session
    
    def create_item(self, request: YourRequest) -> YourResponse:
        # Implementation here
        pass
```

### Phase 6: Test Setup

#### Step 9: Create Test Files (FLAT STRUCTURE)
Create `tests/test_your_service.py`:
```python
import pytest
from unittest.mock import Mock
from services.new_service_name.app.services.your_service import YourService
from services.new_service_name.app.dto.your_dto import YourRequest, YourResponse
from services.new_service_name.app.models.your_model import YourModel

class TestYourService:
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_session = Mock()
        self.mock_logger = Mock()
        self.service = YourService(self.mock_logger, self.mock_session)
    
    def test_create_item_success(self):
        """Test successful item creation"""
        # Your test implementation
        pass
```

**⚠️ CRITICAL RULES FOR TESTS**:
- Tests go directly in `tests/` folder (flat structure)
- NO subdirectories under `tests/`
- NO `__init__.py` in `tests/` directory
- ALWAYS use absolute imports in test files

### Phase 7: VS Code Configuration Update

#### Step 10: Update VS Code Settings
Edit `.vscode/settings.json` and add your service to the pytest arguments:

**ADD these lines:**
```json
{
  "python.testing.pytestArgs": [
    "--rootdir=${workspaceFolder}",
    "--ignore=services/property_service/app",
    "--ignore=services/user_service/app",
    "--ignore=services/new_service_name/app",     // ADD THIS LINE
    "services/property_service/tests",
    "services/user_service/tests",
    "services/new_service_name/tests",            // ADD THIS LINE
    "services/tests"
  ]
}
```

### Phase 8: Validation and Testing

#### Step 11: Validate Import Structure
```bash
# Test model import
python -c "from services.new_service_name.app.models.your_model import YourModel; print('✅ Model import successful')"

# Test service import
python -c "from services.new_service_name.app.services.your_service import YourService; print('✅ Service import successful')"

# Test DTO import
python -c "from services.new_service_name.app.dto.your_dto import YourRequest; print('✅ DTO import successful')"
```

#### Step 12: Validate Test Discovery
```bash
# Test individual service test discovery
pytest --collect-only --rootdir=. services/new_service_name/tests

# Test full workspace test discovery
pytest --collect-only --rootdir=. services/property_service/tests services/user_service/tests services/new_service_name/tests services/tests
```

#### Step 13: Validate VS Code Integration
1. **Restart VS Code** completely
2. Open VS Code Test Explorer (Testing icon in sidebar)
3. Verify your new service tests appear in the test tree
4. Try running a single test to ensure it works

---

## Checklist Before Completing Service

### ✅ Directory Structure Checklist
- [ ] Service created under `services/new_service_name/`
- [ ] All required subdirectories created (`app/`, `tests/`, etc.)
- [ ] `__init__.py` files created in all `app/` subdirectories
- [ ] NO `__init__.py` file in `tests/` directory
- [ ] Tests are in flat structure directly under `tests/`

### ✅ Code Quality Checklist
- [ ] All imports use absolute paths (`services.new_service_name.app...`)
- [ ] SQLAlchemy models include `"extend_existing": True`
- [ ] Service classes follow established patterns
- [ ] DTOs use Pydantic BaseModel
- [ ] Test files use absolute imports

### ✅ Configuration Checklist
- [ ] VS Code `settings.json` updated with new service paths
- [ ] Database configuration follows established pattern
- [ ] All configuration files created (`config.py`, `main.py`, etc.)

### ✅ Validation Checklist
- [ ] All imports work from command line
- [ ] Pytest can discover tests individually
- [ ] Pytest can discover tests in full workspace
- [ ] VS Code Test Explorer shows new tests after restart
- [ ] Can run individual tests successfully

---

## Common Mistakes to Avoid

### ❌ Import Mistakes
```python
# WRONG - Relative imports
from app.models.your_model import YourModel
from app.services.your_service import YourService

# CORRECT - Absolute imports
from services.new_service_name.app.models.your_model import YourModel
from services.new_service_name.app.services.your_service import YourService
```

### ❌ Test Structure Mistakes
```bash
# WRONG - Nested test structure
services/new_service_name/tests/test_new_service_name/test_your_service.py

# CORRECT - Flat test structure
services/new_service_name/tests/test_your_service.py
```

### ❌ SQLAlchemy Mistakes
```python
# WRONG - Missing extend_existing
class YourModel(Base):
    __tablename__ = "your_table"
    __table_args__ = {"schema": "your_schema"}

# CORRECT - With extend_existing
class YourModel(Base):
    __tablename__ = "your_table"
    __table_args__ = {"schema": "your_schema", "extend_existing": True}
```

### ❌ VS Code Configuration Mistakes
- Forgetting to update `settings.json`
- Not restarting VS Code after changes
- Adding service to only one part of pytest args

---

## Quick Reference Commands

### Test Discovery Commands
```bash
# Test single service
pytest --collect-only services/new_service_name/tests

# Test all services
pytest --collect-only services/*/tests

# Run specific test
pytest services/new_service_name/tests/test_your_service.py::TestYourService::test_create_item_success
```

### Import Validation Commands
```bash
# Quick import test
python -c "from services.new_service_name.app.services.your_service import YourService"

# Test SQLAlchemy model
python -c "from services.new_service_name.app.models.your_model import YourModel"
```

---

## Emergency Troubleshooting

### If Tests Don't Appear in VS Code:
1. Check test file names start with `test_`
2. Verify flat directory structure under `tests/`
3. Ensure no `__init__.py` in `tests/` directory
4. Restart VS Code completely
5. Check VS Code Python interpreter is correct

### If Import Errors Occur:
1. Verify all imports use absolute paths
2. Check spelling in import statements
3. Ensure all required `__init__.py` files exist (except in tests)
4. Test imports from command line first

### If SQLAlchemy Errors Occur:
1. Verify `extend_existing=True` in all models
2. Check model imports use absolute paths
3. Ensure Base class import is correct

---

*Document created: August 3, 2025*  
*Repository: Jeeves4Service*  
*For use with monorepo test discovery configuration*
