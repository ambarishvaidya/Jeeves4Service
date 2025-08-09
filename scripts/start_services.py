#!/usr/bin/env python3
"""
Start Services Script for Jeeves4Service

This script starts both the user service and property service in independent
Command Prompt windows, using the virtual environment at the root level.

Services:
- User Service: http://localhost:8000
- Property Service: http://localhost:8001
"""

import os
import sys
import subprocess
import time
import tempfile
from pathlib import Path


def find_virtual_env():
    """Find the virtual environment at the root level."""
    root_dir = Path(__file__).parent
    
    # Common virtual environment directory names
    venv_names = ['venv', '.venv', 'env', '.env']
    
    for venv_name in venv_names:
        venv_path = root_dir / venv_name
        if venv_path.exists():
            # Check for Python executable
            python_exe = venv_path / 'Scripts' / 'python.exe'
            if python_exe.exists():
                return str(python_exe)
    
    # If no virtual environment found, use system Python
    print("Warning: No virtual environment found at root level. Using system Python.")
    return sys.executable


def get_service_info():
    """Get information about the services to start."""
    return [
        {
            'name': 'User Service',
            'module': 'services.user_service.main:app',
            'port': 8000,
            'log_file': 'user_service.log',
            'docs_url': 'http://localhost:8000/docs'
        },
        {
            'name': 'Property Service',
            'module': 'services.property_service.main:app',
            'port': 8001,
            'log_file': 'property_service.log',
            'docs_url': 'http://localhost:8001/docs'
        }
    ]


def start_service_in_new_console(service_info, python_exe, root_dir):
    """Start a service in a new Command Prompt window."""
    service_name = service_info['name']
    module = service_info['module']
    port = service_info['port']
    log_file = service_info['log_file']
    
    print(f"Starting {service_name} on port {port}...")
    
    # Create the uvicorn command string with proper quoting
    uvicorn_cmd_str = f'"{python_exe}" -m uvicorn {module} --host 0.0.0.0 --port {port} --reload --log-level info'
    
    # Create a batch file content that will run in the new console
    batch_content = f'''@echo off
cd /d "{root_dir}"
title {service_name}
echo Starting {service_name}...
echo Service will be available at: http://localhost:{port}
echo API Documentation: {service_info["docs_url"]}
echo Log file: {log_file}
echo.
echo Running command: {uvicorn_cmd_str}
echo.
{uvicorn_cmd_str}
echo.
echo {service_name} has stopped.
pause
'''
    
    # Create a temporary batch file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.bat', delete=False) as batch_file:
        batch_file.write(batch_content)
        batch_file_path = batch_file.name
    
    # Start the service in a new Command Prompt window using the batch file
    subprocess.Popen([
        'cmd', '/c', 'start', 'cmd', '/k', batch_file_path
    ], cwd=root_dir)
    
    print(f"✓ {service_name} started in new console window")
    return True


def check_dependencies():
    """Check if required dependencies are installed."""
    python_exe = find_virtual_env()
    
    try:
        # Check if uvicorn is available
        result = subprocess.run([
            python_exe, '-c', 'import uvicorn; print("uvicorn available")'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            print("Error: uvicorn is not installed in the virtual environment.")
            print("Please install dependencies: pip install -r requirements.txt")
            return False
            
    except subprocess.TimeoutExpired:
        print("Error: Timeout while checking dependencies.")
        return False
    except Exception as e:
        print(f"Error checking dependencies: {e}")
        return False
    
    return True


def main():
    """Main function to start all services."""
    print("=" * 60)
    print("Jeeves4Service - Starting All Services")
    print("=" * 60)
    
    # Get the root directory
    root_dir = str(Path(__file__).parent)
    print(f"Working directory: {root_dir}")
    
    # Find virtual environment
    python_exe = find_virtual_env()
    print(f"Python executable: {python_exe}")
    
    # Check dependencies
    print("\nChecking dependencies...")
    if not check_dependencies():
        print("\nFailed to start services due to missing dependencies.")
        input("Press Enter to exit...")
        return 1
    
    print("✓ Dependencies check passed")
    
    # Get service information
    services = get_service_info()
    
    print(f"\nStarting {len(services)} services...")
    print("-" * 40)
    
    # Start each service
    started_services = []
    for service in services:
        try:
            if start_service_in_new_console(service, python_exe, root_dir):
                started_services.append(service)
                time.sleep(2)  # Brief delay between service starts
        except Exception as e:
            print(f"✗ Failed to start {service['name']}: {e}")
    
    print("-" * 40)
    print(f"\nStarted {len(started_services)} out of {len(services)} services")
    
    if started_services:
        print("\nServices Overview:")
        for service in started_services:
            print(f"  • {service['name']}: http://localhost:{service['port']}")
            print(f"    Docs: {service['docs_url']}")
            print(f"    Logs: {service['log_file']}")
        
        print("\nAll services are starting in separate console windows.")
        print("You can close this window - the services will continue running.")
        print("\nTo stop a service, close its respective console window or press Ctrl+C in it.")
    else:
        print("\nNo services were started successfully.")
        input("Press Enter to exit...")
        return 1
    
    input("\nPress Enter to exit this startup script...")
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nStartup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        input("Press Enter to exit...")
        sys.exit(1)
