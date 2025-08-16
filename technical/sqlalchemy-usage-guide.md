# SQLAlchemy Usage Guide

## Table of Contents
1. [Fundamentals](#fundamentals)
2. [Architectural Decisions](#architectural-decisions)
3. [Engine Creation and Session Management](#engine-creation-and-session-management)
4. [Project-Specific Implementation](#project-specific-implementation)
5. [Database Schema Management](#database-schema-management)
6. [PostgreSQL Full-Text Search](#postgresql-full-text-search)
7. [Testing with SQLAlchemy](#testing-with-sqlalchemy)
8. [Design Patterns and Alternatives](#design-patterns-and-alternatives)
9. [Best Practices and Common Pitfalls](#best-practices-and-common-pitfalls)

## Fundamentals

### What is SQLAlchemy?

SQLAlchemy is a Python SQL toolkit and Object-Relational Mapping (ORM) library that provides a full suite of tools for working with databases. It consists of two main components:

1. **Core**: Low-level database abstraction (Expression Language)
2. **ORM**: High-level object-relational mapping

### Why Use SQLAlchemy?

- **Database Abstraction**: Write database-agnostic code
- **Security**: Built-in SQL injection protection
- **Performance**: Connection pooling and query optimization
- **Flexibility**: Support for raw SQL when needed
- **Migration Support**: Integration with Alembic for schema management

## Architectural Decisions

### Why SQLAlchemy Over Other ORMs?

#### Alternative 1: Django ORM
```python
# ❌ Django ORM (What we could have used)
from django.db import models

class HouseholdItem(models.Model):
    product_name = models.CharField(max_length=255, null=True)
    general_name = models.CharField(max_length=255)
    quantity = models.IntegerField(null=True)
    
    class Meta:
        db_table = 'household_items'
```

**Why we chose SQLAlchemy instead:**
- **Framework Independence**: Not tied to Django web framework
- **Flexibility**: More control over SQL generation
- **Raw SQL Support**: Easy to use complex PostgreSQL features
- **Migration Control**: Alembic gives more control than Django migrations

#### Alternative 2: Peewee ORM
```python
# ❌ Peewee ORM (Another option we considered)
from peewee import Model, CharField, IntegerField

class HouseholdItem(Model):
    product_name = CharField(null=True)
    general_name = CharField()
    quantity = IntegerField(null=True)
    
    class Meta:
        database = db
        table_name = 'household_items'
```

**Why SQLAlchemy is better for our use case:**
- **Enterprise Features**: Better connection pooling and transaction management
- **Complex Queries**: Better support for complex joins and subqueries
- **PostgreSQL Integration**: Excellent support for PostgreSQL-specific features
- **Community**: Larger community and more resources

#### Alternative 3: Raw SQL with psycopg2
```python
# ❌ Raw SQL approach (What we avoided)
import psycopg2

def add_household_item(product_name, general_name, quantity):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO household.items (product_name, general_name, quantity)
            VALUES (%s, %s, %s) RETURNING id
        """, (product_name, general_name, quantity))
        
        item_id = cursor.fetchone()[0]
        conn.commit()
        return item_id
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()
```

**Why SQLAlchemy ORM is better:**
- **Object Mapping**: Work with Python objects instead of raw SQL
- **Automatic SQL Generation**: Less error-prone than hand-written SQL
- **Query Builder**: Type-safe query construction
- **Relationship Management**: Automatic handling of foreign keys and joins

### Database Architecture: Multi-Schema Approach

#### Our Choice: Schema Separation
```python
# ✅ Our approach: Separate schemas per service
# services/user_service/app/models/user.py
class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "user"}  # user.users table

# services/property_service/app/models/property.py  
class Property(Base):
    __tablename__ = "properties"
    __table_args__ = {"schema": "property"}  # property.properties table

# services/household_service/app/models/household.py
class Household(Base):
    __tablename__ = "items"
    __table_args__ = {"schema": "household"}  # household.items table
```

#### Alternative Approaches We Considered

**Alternative 1: Shared Schema**
```python
# ❌ What we could have done: Everything in one schema
class User(Base):
    __tablename__ = "users"  # public.users

class Property(Base):
    __tablename__ = "properties"  # public.properties
    
class HouseholdItem(Base):
    __tablename__ = "household_items"  # public.household_items
```

**Why we rejected this:**
- **Naming Conflicts**: Table names might clash as project grows
- **Permissions**: Harder to set service-specific database permissions
- **Organization**: All tables mixed together
- **Migration Conflicts**: Services could interfere with each other's migrations

**Alternative 2: Separate Databases**
```python
# ❌ Another option: Separate databases per service
USER_DATABASE_URL = "postgresql://user:pass@localhost/user_service_db"
PROPERTY_DATABASE_URL = "postgresql://user:pass@localhost/property_service_db"
HOUSEHOLD_DATABASE_URL = "postgresql://user:pass@localhost/household_service_db"
```

**Why schema separation is better:**
- **Shared Infrastructure**: Single PostgreSQL instance to manage
- **Cross-Service Queries**: Can join across schemas if needed
- **Backup Simplicity**: Single database backup
- **Cost Efficiency**: Lower resource usage than multiple databases

### Engine Configuration Strategy

#### Our Approach: Service-Specific Engines
```python
# ✅ Each service has its own engine configuration
# services/user_service/app/db/session.py
engine = create_engine(DATABASE_URL, echo=True, future=True)

# services/property_service/app/db/session.py  
engine = create_engine(DATABASE_URL)  # Different config per service

# services/household_service/app/db/session.py
engine = create_engine(DATABASE_URL, echo=True, future=True)
```

**Why this pattern:**
- **Service Isolation**: Each service controls its own database configuration
- **Independent Scaling**: Can tune connection pools per service
- **Debugging Flexibility**: Can enable SQL logging for specific services
- **Deployment Flexibility**: Services can use different database credentials

#### Alternative: Shared Engine
```python
# ❌ What we could have done: Single shared engine
# services/shared/database.py
shared_engine = create_engine(DATABASE_URL)

# All services import and use the same engine
from services.shared.database import shared_engine
```

**Why we avoided this:**
- **Tight Coupling**: Services become dependent on shared configuration
- **Scaling Issues**: Cannot tune connection pools per service
- **Testing Complexity**: Harder to mock database for individual services

## Engine Creation and Session Management

### Engine: The Heart of SQLAlchemy

The Engine is SQLAlchemy's core interface to the database. It manages:
- Database connections
- Connection pooling
- SQL dialect specifics
- Transaction boundaries

### Why Engines Matter: The Connection Problem

#### The Problem Without Proper Engine Management
```python
# ❌ What happens without proper engine configuration
import psycopg2

def get_data_bad():
    # New connection every time - very inefficient!
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    data = cursor.fetchall()
    conn.close()  # Connection destroyed
    return data

def save_data_bad(user_data):
    # Another new connection - expensive!
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (...) VALUES (...)", user_data)
    conn.commit()
    conn.close()
    
# If called 100 times = 200 database connections created and destroyed!
```

**Problems with this approach:**
1. **Performance**: Creating connections is expensive (100-200ms each)
2. **Resource Waste**: Database server handles too many connections
3. **Reliability**: No connection validation or retry logic
4. **Scalability**: Database connection limits reached quickly

#### Our Solution: SQLAlchemy Engine with Connection Pooling
```python
# ✅ SQLAlchemy engine solves these problems
from sqlalchemy import create_engine

engine = create_engine(
    DATABASE_URL,
    pool_size=20,           # Maintain 20 persistent connections
    max_overflow=30,        # Allow 30 additional connections when needed
    pool_pre_ping=True,     # Validate connections before use
    pool_recycle=3600       # Refresh connections every hour
)

# Now all operations use the connection pool
def get_data_good():
    with engine.connect() as conn:  # Gets connection from pool
        result = conn.execute("SELECT * FROM users")
        return result.fetchall()
    # Connection returned to pool, not destroyed!
```

### Engine Configuration Deep Dive

#### How the Engine is Created

```python
from sqlalchemy import create_engine

# Basic engine creation
engine = create_engine(DATABASE_URL)

# Production-ready engine configuration
engine = create_engine(
    DATABASE_URL,
    echo=True,              # Log all SQL statements (development)
    future=True,            # Use SQLAlchemy 2.0 style
    pool_pre_ping=True,     # Validate connections before use  
    pool_recycle=3600,      # Recycle connections after 1 hour
    pool_size=20,           # Number of connections to maintain
    max_overflow=30,        # Additional connections when needed
    pool_timeout=30,        # Timeout when getting connection from pool
    connect_args={          # PostgreSQL-specific arguments
        "sslmode": "prefer",
        "connect_timeout": 10
    }
)
```

#### Configuration Options Explained

**`echo=True` - SQL Logging**
```python
# With echo=True, you see all SQL:
engine = create_engine(DATABASE_URL, echo=True)

# Output in logs:
# INFO sqlalchemy.engine.Engine SELECT users.id, users.email FROM users WHERE users.id = %(id_1)s
# INFO sqlalchemy.engine.Engine {'id_1': 123}
```

**Why we use this:**
- **Development**: See exactly what SQL is being generated
- **Debugging**: Identify slow or problematic queries
- **Learning**: Understand how ORM translates to SQL

**When to disable:**
- **Production**: Too verbose for production logs
- **Performance**: Logging overhead in high-traffic scenarios

**`future=True` - SQLAlchemy 2.0 Style**
```python
# Enables modern SQLAlchemy patterns
engine = create_engine(DATABASE_URL, future=True)

# Allows for cleaner syntax:
with engine.begin() as conn:
    result = conn.execute(text("SELECT * FROM users"))
```

**`pool_pre_ping=True` - Connection Validation**
```python
# Validates connections before use
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
```

**What this prevents:**
```python
# Without pool_pre_ping, this could happen:
def get_user(user_id):
    session = SessionLocal()
    # This might fail if connection was closed by database
    user = session.query(User).get(user_id)  # DatabaseError!
    return user

# With pool_pre_ping:
def get_user(user_id):
    session = SessionLocal()
    # Connection is validated first, replaced if invalid
    user = session.query(User).get(user_id)  # Always works!
    return user
```

#### Connection String Structure and Reasoning

```python
# Our connection string format
DATABASE_URL = "postgresql+psycopg2://python:python@localhost:5432/J4S.Application"
#              ↑          ↑        ↑     ↑         ↑      ↑
#              dialect    driver   user  password  host   port/database
```

**Component breakdown:**
- **`postgresql`**: Database type (could be mysql, sqlite, etc.)
- **`psycopg2`**: Python database driver (fastest PostgreSQL driver)
- **`python:python`**: Username and password (development credentials)
- **`localhost:5432`**: Host and port (PostgreSQL default port)
- **`J4S.Application`**: Database name

**Alternative drivers we considered:**
```python
# Option 1: asyncpg (async driver)
DATABASE_URL = "postgresql+asyncpg://user:pass@host/db"
# Pros: Better performance for async applications
# Cons: Our application is synchronous, would require major changes

# Option 2: pg8000 (pure Python driver)  
DATABASE_URL = "postgresql+pg8000://user:pass@host/db"
# Pros: No C dependencies, easier deployment
# Cons: Slower than psycopg2

# Our choice: psycopg2 (C-based driver)
DATABASE_URL = "postgresql+psycopg2://user:pass@host/db"  
# Pros: Fastest, most mature, best PostgreSQL feature support
# Cons: Requires C compilation, slightly harder deployment
```

### Session: The ORM Interface

Sessions provide the interface between your Python objects and the database. They:
- Track object changes (dirty tracking)
- Manage transactions (commit/rollback)
- Execute queries
- Handle lazy loading
- Implement identity map pattern

#### Session Creation Pattern Evolution

**Basic Pattern (Where we started):**
```python
from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()
```

**Enhanced Pattern (Current implementation):**
```python
from sqlalchemy.orm import sessionmaker

# Create session factory with specific configuration
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,    # Don't automatically flush changes
    autocommit=False    # Use explicit transactions
)

# Create session instance
session = SessionLocal()
```

**Why these specific settings:**

**`autoflush=False`**
```python
# With autoflush=True (default), this happens:
session = SessionLocal()  # autoflush=True
user = User(email="test@example.com")
session.add(user)
# Automatic flush happens here ↓
count = session.query(User).count()  # SQL: SELECT COUNT(*) FROM users
print(f"User ID: {user.id}")  # user.id is available because of autoflush

# With autoflush=False (our choice):
session = SessionLocal()  # autoflush=False  
user = User(email="test@example.com")
session.add(user)
# No automatic flush ↓
count = session.query(User).count()  # Doesn't include new user yet
print(f"User ID: {user.id}")  # None - must flush manually
session.flush()  # Explicit flush
print(f"User ID: {user.id}")  # Now has ID
```

**Why we chose `autoflush=False`:**
- **Predictability**: We control exactly when SQL is executed
- **Performance**: Avoid unnecessary SQL statements
- **Testing**: Easier to test without side effects
- **Debugging**: Explicit control over when database is accessed

**`autocommit=False`**
```python
# With autocommit=True, each statement is immediately committed:
session = SessionLocal()  # autocommit=True
user = User(email="test@example.com")
session.add(user)
session.flush()  # User is immediately committed to database!
# If error occurs here, user is already saved (bad!)

# With autocommit=False (our choice):
session = SessionLocal()  # autocommit=False
user = User(email="test@example.com") 
session.add(user)
session.flush()  # User is in transaction, not committed yet
# If error occurs here, can rollback everything
session.commit()  # Explicit commit
```

#### Session Lifecycle and Transaction Management

```python
def database_operation():
    session = SessionLocal()
    try:
        # Perform database operations
        result = session.query(Model).filter(...).all()
        session.commit()  # Explicit commit
        return result
    except Exception as e:
        session.rollback()  # Rollback on error
        raise
    finally:
        session.close()    # Always clean up
```

**Why this pattern:**

1. **Transaction Safety**: Either all operations succeed or all are rolled back
2. **Resource Management**: Session is always closed
3. **Error Handling**: Explicit error handling and cleanup
4. **Predictability**: Same pattern used everywhere

#### Session Scoping Strategies

**Our Approach: Request-Scoped Sessions**
```python
# In FastAPI applications
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/users")
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    # Each request gets its own session
    user = User(**user_data.dict())
    db.add(user)
    db.commit()
    return user
```

**Alternative: Thread-Local Sessions**
```python
# ❌ What we could have used but avoided
from sqlalchemy.orm import scoped_session

SessionLocal = scoped_session(sessionmaker(bind=engine))

def create_user(user_data):
    # Thread-local session
    session = SessionLocal()
    user = User(**user_data)
    session.add(user)
    session.commit()
    # No explicit cleanup - handled by scoped_session
```

**Why we chose request-scoped over thread-local:**
- **Explicit Control**: Clear session lifecycle
- **Testing**: Easier to mock and test
- **FastAPI Integration**: Works well with dependency injection
- **Debugging**: Can easily track session usage
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()
```

## Project-Specific Implementation

### Multi-Service Architecture

This project uses a microservices architecture with separate SQLAlchemy configurations per service:

1. **User Service** (`services/user_service/`)
2. **Property Service** (`services/property_service/`)
3. **Household Service** (`services/household_service/`)

### Service Configuration Pattern

Each service follows the same structure:

```
service_name/
├── app/
│   ├── config.py           # Database URL configuration
│   ├── db/
│   │   ├── base.py         # Declarative base
│   │   └── session.py      # Engine and session creation
│   └── models/             # ORM models
├── alembic/                # Database migrations
└── alembic.ini            # Alembic configuration
```

### Configuration Files

#### config.py
```python
"""Application configuration module."""
import os

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+psycopg2://python:python@localhost:5432/J4S.Application"
)
```

#### db/base.py
```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```

#### db/session.py
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from services.household_service.app.config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
```

### Schema Separation

Each service uses a separate PostgreSQL schema:
- User Service: `user` schema
- Property Service: `property` schema
- Household Service: `household` schema

This provides:
- **Isolation**: Services can't accidentally access each other's data
- **Organization**: Related tables are grouped together
- **Migration Management**: Independent schema evolution

## Database Schema Management

### Alembic Integration

Alembic is SQLAlchemy's migration tool, handling schema changes over time.

#### Configuration per Service

Each service has its own Alembic configuration:

```python
# alembic/env.py
from services.household_service.app.config import DATABASE_URL
from services.household_service.app.db.base import Base
from services.household_service.app.models import household

target_metadata = Base.metadata
```

#### Schema-Specific Migrations

```python
def run_migrations_offline() -> None:
    url = DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        include_schemas=True,
        include_object=lambda object, name, type_, reflected, compare_to: (
            object.schema == "household" if type_ == "table" else True
        ),
        dialect_opts={"paramstyle": "named"},
        version_table="alembic_version_household_service",
        version_table_schema="household"
    )
```

### Model Definition

#### Base Model Pattern

```python
from sqlalchemy import Column, Integer, String
from services.household_service.app.db.base import Base

class Household(Base):
    __tablename__ = "items"
    __table_args__ = {"schema": "household", "extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, index=True, nullable=True)
    general_name = Column(String, index=True, nullable=False)
    quantity = Column(Integer, nullable=True)
    storage_id = Column(Integer)
    property_id = Column(Integer, index=True)
```

## PostgreSQL Full-Text Search

### TSVECTOR Implementation

The project implements PostgreSQL's full-text search using TSVECTOR columns:

```python
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy import Column, Index

class Household(Base):
    # ... other columns ...
    search_vector = Column(TSVECTOR)
    
    __table_args__ = (
        Index("ix_household_search_idx", "search_vector", postgresql_using="gin"),
        {"schema": "household", "extend_existing": True"}
    )
```

### GIN Index for Performance

The project uses GIN (Generalized Inverted Index) for fast full-text searches:

```python
Index("ix_household_search_idx", "search_vector", postgresql_using="gin")
```

### Search Implementation

#### Query Construction

```python
from sqlalchemy import func, text

def search_items(session, search_terms):
    # Convert search terms to tsquery format
    query_text = " & ".join(search_terms)
    
    # Perform full-text search
    results = session.query(Household).filter(
        Household.search_vector.op("@@")(func.plainto_tsquery("english", query_text))
    ).all()
    
    return results
```

#### Search Vector Updates

```python
# Update search vector when adding/modifying items
update_stmt = text("""
    UPDATE household.items 
    SET search_vector = to_tsvector('english', 
        COALESCE(product_name, '') || ' ' || COALESCE(general_name, '')
    )
    WHERE id = :item_id
""")

session.execute(update_stmt, {"item_id": item.id})
```

### NLP Integration with spaCy

The project enhances search with spaCy for lemmatization:

```python
import spacy

nlp = spacy.load("en_core_web_sm")

def lemmatize_search_terms(search_text):
    """Convert search terms to their base forms"""
    doc = nlp(search_text)
    lemmatized_terms = []
    
    for token in doc:
        if not token.is_stop and not token.is_punct and token.text.strip():
            lemmatized_terms.append(token.lemma_.lower())
    
    return lemmatized_terms
```

## Testing with SQLAlchemy

### Mock Session Pattern

```python
import pytest
from unittest.mock import Mock, MagicMock
from sqlalchemy.orm import Session

@pytest.fixture
def mock_session():
    """Create a mock SQLAlchemy session for testing"""
    session = Mock(spec=Session)
    session.query.return_value = session
    session.filter.return_value = session
    session.all.return_value = []
    session.first.return_value = None
    session.commit.return_value = None
    session.rollback.return_value = None
    session.close.return_value = None
    return session
```

### Testing Database Operations

```python
def test_add_item_success(mock_session):
    """Test successful item addition"""
    # Arrange
    mock_session.add.return_value = None
    mock_session.commit.return_value = None
    
    service = AddHouseholdItemService(mock_session)
    request = AddHouseholdItemRequestDto(
        product_name="Test Product",
        general_name="Test General",
        quantity=5,
        storage_id=1,
        property_id=1
    )
    
    # Act
    result = service.add_item(request)
    
    # Assert
    assert result.success is True
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
```

## Best Practices and Common Pitfalls

### Engine Configuration

#### Best Practices

```python
# Use connection pooling for production
engine = create_engine(
    DATABASE_URL,
    pool_size=20,           # Number of connections to maintain
    max_overflow=30,        # Additional connections when needed
    pool_pre_ping=True,     # Validate connections
    pool_recycle=3600,      # Recycle connections every hour
    echo=False              # Disable SQL logging in production
)
```

#### Development vs Production Settings

```python
# Development - with SQL logging
engine = create_engine(DATABASE_URL, echo=True, future=True)

# Production - optimized for performance
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True
)
```

### Session Management

#### Best Practices

1. **Always use try/except/finally blocks**
```python
session = SessionLocal()
try:
    # Database operations
    result = perform_operation(session)
    session.commit()
    return result
except Exception as e:
    session.rollback()
    logger.error(f"Database operation failed: {e}")
    raise
finally:
    session.close()
```

2. **Use context managers when possible**
```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

3. **Avoid session sharing between requests**
   - Each request should have its own session
   - Don't store sessions as class attributes

#### Common Pitfalls

1. **Forgetting to close sessions**
   - Leads to connection pool exhaustion
   - Always use finally blocks or context managers

2. **Not handling rollback on errors**
   - Failed transactions can leave sessions in invalid state
   - Always rollback on exceptions

3. **Mixing session instances**
   - Objects are bound to specific sessions
   - Don't pass objects between different sessions

### Full-Text Search Optimization

#### Performance Tips

1. **Use GIN indexes for TSVECTOR columns**
```python
Index("ix_search_idx", "search_vector", postgresql_using="gin")
```

2. **Limit search result sets**
```python
results = session.query(Model)\
    .filter(Model.search_vector.op("@@")(query))\
    .limit(50)\
    .all()
```

3. **Use ranking for relevance**
```python
from sqlalchemy import func

results = session.query(
    Model,
    func.ts_rank(Model.search_vector, query).label("rank")
).filter(
    Model.search_vector.op("@@")(query)
).order_by("rank DESC").all()
```

### Migration Management

#### Best Practices

1. **Generate migrations for all model changes**
```bash
alembic revision --autogenerate -m "Description of change"
```

2. **Review generated migrations before applying**
   - Auto-generation isn't perfect
   - Manual review prevents data loss

3. **Use separate migration environments**
   - Development, staging, production
   - Test migrations thoroughly

4. **Keep migrations small and focused**
   - One logical change per migration
   - Easier to debug and rollback

### Error Handling

#### Database Connection Errors

```python
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

try:
    session.add(new_item)
    session.commit()
except IntegrityError as e:
    session.rollback()
    logger.error(f"Constraint violation: {e}")
    raise ValueError("Item already exists or constraint violated")
except SQLAlchemyError as e:
    session.rollback()
    logger.error(f"Database error: {e}")
    raise RuntimeError("Database operation failed")
```

#### Connection Pool Monitoring

```python
# Monitor connection pool status
pool = engine.pool
logger.info(f"Pool size: {pool.size()}")
logger.info(f"Checked out connections: {pool.checkedout()}")
logger.info(f"Checked in connections: {pool.checkedin()}")
```

This comprehensive guide covers SQLAlchemy usage in the Jeeves4Service project, from fundamental concepts to advanced implementations. The project's multi-service architecture with PostgreSQL full-text search provides a robust foundation for scalable microservices development.
