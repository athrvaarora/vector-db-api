#!/usr/bin/env python3
"""
Setup script for library endpoint tests.
Installs dependencies and verifies the test environment.
"""

import sys
import subprocess
import importlib.util
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True


def install_dependencies():
    """Install required test dependencies."""
    print("\n📦 Installing test dependencies...")
    
    requirements_file = Path(__file__).parent.parent / "requirements.txt"
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
            return True
        else:
            print(f"❌ Failed to install dependencies: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False


def verify_imports():
    """Verify that all required modules can be imported."""
    print("\n🔍 Verifying imports...")
    
    required_modules = ['requests', 'colorama', 'psutil']
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - not installed")
            return False
    
    return True


def verify_project_structure():
    """Verify that the project structure is correct."""
    print("\n📁 Verifying project structure...")
    
    project_root = Path(__file__).parent.parent.parent
    required_paths = [
        project_root / "app" / "main.py",
        project_root / "app" / "api" / "endpoints.py",
        project_root / "tests" / "libraries" / "test_utils.py",
        project_root / "tests" / "libraries" / "test_data.py",
    ]
    
    for path in required_paths:
        if path.exists():
            print(f"✅ {path.relative_to(project_root)}")
        else:
            print(f"❌ {path.relative_to(project_root)} - missing")
            return False
    
    return True


def main():
    """Run the complete setup process."""
    print("🧪 VECTOR DATABASE API - TEST SETUP")
    print("=" * 50)
    
    success = True
    
    # Check Python version
    success &= check_python_version()
    
    # Install dependencies
    success &= install_dependencies()
    
    # Verify imports
    success &= verify_imports()
    
    # Verify project structure
    success &= verify_project_structure()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Setup completed successfully!")
        print("\nYou can now run tests:")
        print("  • Individual tests: python3 tests/libraries/test_create_library.py")
        print("  • All tests: python3 tests/libraries/run_all_tests.py")
    else:
        print("❌ Setup failed. Please fix the issues above.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())