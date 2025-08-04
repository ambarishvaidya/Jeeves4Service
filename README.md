# Jeeves4Service - Monorepo

This is a monorepo containing multiple microservices for the Jeeves4Service application.

## Structure

```
Jeeves4Service/
├── requirements.txt          # All dependencies managed here
├── services/
│   ├── user_service/        # User management service
│   ├── property_service/    # Property management service
│   └── shared/              # Shared libraries
│       ├── j4s_crypto_lib/  # Cryptographic utilities
│       └── j4s_logging_lib/ # Logging utilities
├── j4s_client/              # Client libraries
└── tests/                   # Integration tests
```

## Setup

1. **Create a virtual environment at the root level:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   # or
   source .venv/bin/activate  # On Unix/macOS
   ```

2. **Install all dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install shared libraries in development mode:**
   ```bash
   pip install -e services/shared/j4s_crypto_lib
   pip install -e services/shared/j4s_logging_lib
   ```

## Running Services

### User Service
```bash
cd services/user_service
python main.py
```

### Property Service
```bash
cd services/property_service
python main.py
```

## Development

All dependencies are managed in the root `requirements.txt` file. Individual services no longer maintain their own virtual environments or requirements files.

### Running Tests
```bash
# Run all tests
pytest

# Run specific service tests
pytest services/user_service/tests/
pytest services/property_service/tests/
```

### Code Formatting
```bash
black .
isort .
```

## Migration from Individual Environments

The monorepo structure consolidates all dependencies at the root level. Individual service `requirements.txt` and `pyproject.toml` files have been removed since services are run directly rather than installed as packages. Only the shared libraries retain their `pyproject.toml` files as they are installed as editable packages.
