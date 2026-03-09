"""
Test Script - Verify Installation and Imports
Run this to ensure all dependencies are properly installed
"""

import sys
from importlib import import_module

# List of required packages
REQUIRED_PACKAGES = [
    ('fastapi', 'FastAPI'),
    ('uvicorn', 'Uvicorn'),
    ('pydantic', 'Pydantic'),
    ('pydantic_settings', 'Pydantic Settings'),
    ('sqlalchemy', 'SQLAlchemy'),
    ('asyncpg', 'asyncpg'),
    ('redis', 'Redis'),
    ('httpx', 'HTTPX'),
    ('dotenv', 'python-dotenv'),
    ('email_validator', 'email-validator'),
]

def test_imports():
    """Test if all required packages can be imported"""
    print("=" * 60)
    print("Testing Package Imports")
    print("=" * 60)
    
    all_passed = True
    
    for package_name, display_name in REQUIRED_PACKAGES:
        try:
            module = import_module(package_name)
            version = getattr(module, '__version__', 'unknown')
            print(f"✓ {display_name:.<30} {version}")
        except ImportError as e:
            print(f"✗ {display_name:.<30} FAILED: {e}")
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("✓ All required packages are installed!")
        print()
        print("Python version:", sys.version)
        print()
        print("Next steps:")
        print("1. Start PostgreSQL and create databases (or use docker-compose)")
        print("2. Start Redis (or use docker-compose)")
        print("3. Run services with: python <service-folder>/main.py")
        print("   or use: docker-compose up --build")
        return 0
    else:
        print("✗ Some packages are missing. Please install them:")
        print("   pip install -r asset-service/requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(test_imports())
