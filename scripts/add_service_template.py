#!/usr/bin/env python3
"""
Service Template Generator for Jeeves4Service

This script creates a new service with the standard folder structure
following the pattern used by user_service and property_service.
"""

import os
import re
import sys
from pathlib import Path


def validate_service_name(name):
    """
    Validate service name:
    - No spaces
    - Valid Python identifier rules
    - Not empty
    """
    if not name:
        return False, "Service name cannot be empty"
    
    if ' ' in name:
        return False, "Service name cannot contain spaces"
    
    # Check if it's a valid Python identifier (without _service suffix for now)
    base_name = name.replace('_service', '') if name.endswith('_service') else name
    if not base_name.isidentifier():
        return False, "Service name must be a valid Python identifier (alphanumeric and underscores only, cannot start with number)"
    
    return True, ""


def normalize_service_name(name):
    """
    Normalize service name:
    - Ensure it ends with _service
    - Convert to lowercase
    """
    name = name.lower()
    if not name.endswith('_service'):
        name = f"{name}_service"
    return name


def check_service_exists(service_name, services_dir):
    """Check if service already exists."""
    service_path = services_dir / service_name
    return service_path.exists()


def create_init_file(path):
    """Create an empty __init__.py file."""
    init_file = path / "__init__.py"
    init_file.touch()
    print(f"  Created: {init_file.relative_to(Path.cwd())}")


def create_service_structure(service_name, services_dir):
    """Create the complete service folder structure."""
    service_path = services_dir / service_name
    
    print(f"\nCreating service structure for '{service_name}'...")
    
    # Create main service directory
    service_path.mkdir(exist_ok=True)
    print(f"Created: {service_path.relative_to(Path.cwd())}")
    
    # Create main.py (empty)
    main_py = service_path / "main.py"
    main_py.touch()
    print(f"  Created: {main_py.relative_to(Path.cwd())}")
    
    # Create alembic directory (empty)
    alembic_dir = service_path / "alembic"
    alembic_dir.mkdir(exist_ok=True)
    print(f"  Created: {alembic_dir.relative_to(Path.cwd())}")
    
    # Create app directory with subdirectories
    app_dir = service_path / "app"
    app_dir.mkdir(exist_ok=True)
    print(f"  Created: {app_dir.relative_to(Path.cwd())}")
    create_init_file(app_dir)
    
    # Create app subdirectories
    app_subdirs = ["core", "db", "di", "dto", "models", "services"]
    for subdir in app_subdirs:
        subdir_path = app_dir / subdir
        subdir_path.mkdir(exist_ok=True)
        print(f"  Created: {subdir_path.relative_to(Path.cwd())}")
        create_init_file(subdir_path)
    
    # Create routes directory
    routes_dir = service_path / "routes"
    routes_dir.mkdir(exist_ok=True)
    print(f"  Created: {routes_dir.relative_to(Path.cwd())}")
    create_init_file(routes_dir)
    
    # Create tests directory
    tests_dir = service_path / "tests"
    tests_dir.mkdir(exist_ok=True)
    print(f"  Created: {tests_dir.relative_to(Path.cwd())}")
    create_init_file(tests_dir)
    
    print(f"\n✅ Service '{service_name}' created successfully!")
    print(f"📁 Location: {service_path.relative_to(Path.cwd())}")


def main():
    """Main function to create a new service."""
    print("🚀 Jeeves4Service - Service Template Generator")
    print("=" * 50)
    
    # Get the root directory and services directory
    root_dir = Path(__file__).parent.parent
    services_dir = root_dir / "services"
    
    if not services_dir.exists():
        print(f"❌ Services directory not found: {services_dir}")
        sys.exit(1)
    
    # Get service name from user
    while True:
        service_name = input("\n📝 Enter the service name: ").strip()
        
        # Validate service name
        is_valid, error_msg = validate_service_name(service_name)
        if not is_valid:
            print(f"❌ Invalid service name: {error_msg}")
            continue
        
        # Normalize service name
        normalized_name = normalize_service_name(service_name)
        
        if normalized_name != service_name:
            print(f"📋 Service name normalized to: {normalized_name}")
        
        # Check if service already exists
        if check_service_exists(normalized_name, services_dir):
            print(f"❌ Service '{normalized_name}' already exists!")
            print("   Choose a different name or manually remove the existing service.")
            continue
        
        # Confirm creation
        print(f"\n📦 Ready to create service: {normalized_name}")
        confirm = input("Continue? (y/n): ").strip().lower()
        
        if confirm in ['y', 'yes']:
            break
        elif confirm in ['n', 'no']:
            print("❌ Service creation cancelled.")
            sys.exit(0)
        else:
            print("Please enter 'y' or 'n'")
    
    try:
        # Create the service structure
        create_service_structure(normalized_name, services_dir)
        
        print(f"\n🎉 Next steps:")
        print(f"   1. Navigate to: services/{normalized_name}/")
        print(f"   2. Edit main.py to add your FastAPI application")
        print(f"   3. Add your routes in the routes/ directory")
        print(f"   4. Add your models in the app/models/ directory")
        print(f"   5. Add your services in the app/services/ directory")
        
    except Exception as e:
        print(f"❌ Error creating service: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
