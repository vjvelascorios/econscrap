#!/usr/bin/env python3
"""
Test script to validate that all dependencies and scripts work correctly
"""

import sys
import importlib.util
import subprocess
from pathlib import Path

def test_dependencies():
    """Test that all required dependencies are installed"""
    dependencies = [
        'requests',
        'beautifulsoup4', 
        'pandas',
        'pathlib',
        'tqdm'
    ]
    
    print("Testing dependencies...")
    failed = []
    
    for dep in dependencies:
        try:
            if dep == 'beautifulsoup4':
                import bs4
            else:
                __import__(dep)
            print(f"✅ {dep} - OK")
        except ImportError:
            print(f"❌ {dep} - MISSING")
            failed.append(dep)
    
    return len(failed) == 0, failed

def test_script_syntax():
    """Test that all Python scripts have valid syntax"""
    scripts_dir = Path("scripts")
    scripts = list(scripts_dir.glob("*.py"))
    
    print(f"\nTesting syntax for {len(scripts)} scripts...")
    failed = []
    
    for script in scripts:
        try:
            with open(script, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Try to compile the code
            compile(code, str(script), 'exec')
            print(f"✅ {script.name} - Syntax OK")
            
        except SyntaxError as e:
            print(f"❌ {script.name} - Syntax Error: {e}")
            failed.append(script.name)
        except Exception as e:
            print(f"⚠️  {script.name} - Other Error: {e}")
            failed.append(script.name)
    
    return len(failed) == 0, failed

def test_directories():
    """Test that required directories exist or can be created"""
    required_dirs = [
        "reports and files/banxico_library_updates",
        "reports and files/banxico_quarterly_reports", 
        "reports and files/banxico_regional_reports",
        "reports and files/private_sector_expectations"
    ]
    
    print(f"\nTesting directories...")
    failed = []
    
    for dir_path in required_dirs:
        try:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            print(f"✅ {dir_path} - OK")
        except Exception as e:
            print(f"❌ {dir_path} - Error: {e}")
            failed.append(dir_path)
    
    return len(failed) == 0, failed

def main():
    """Run all tests"""
    print("🔍 Running workflow validation tests...\n")
    
    all_passed = True
    
    # Test dependencies
    deps_ok, deps_failed = test_dependencies()
    if not deps_ok:
        print(f"\n❌ Missing dependencies: {', '.join(deps_failed)}")
        all_passed = False
    
    # Test script syntax
    syntax_ok, syntax_failed = test_script_syntax()
    if not syntax_ok:
        print(f"\n❌ Scripts with syntax errors: {', '.join(syntax_failed)}")
        all_passed = False
    
    # Test directories
    dirs_ok, dirs_failed = test_directories()
    if not dirs_ok:
        print(f"\n❌ Directory creation failed: {', '.join(dirs_failed)}")
        all_passed = False
    
    # Final result
    print("\n" + "="*50)
    if all_passed:
        print("✅ ALL TESTS PASSED - Workflow should work correctly!")
        return 0
    else:
        print("❌ SOME TESTS FAILED - Please fix the issues above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
