#!/usr/bin/env python3
"""
Debug script for GitHub Actions workflow
This script will help identify issues when running in CI/CD environment
"""

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

def print_env_info():
    """Print environment information"""
    print("🔍 Environment Information")
    print("=" * 50)
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python executable: {sys.executable}")
    print(f"Date/Time: {datetime.now()}")
    
    # GitHub Actions specific variables
    github_vars = [
        'GITHUB_WORKFLOW',
        'GITHUB_RUN_ID', 
        'GITHUB_EVENT_NAME',
        'GITHUB_REPOSITORY',
        'GITHUB_REF'
    ]
    
    print("\n🔧 GitHub Actions Variables:")
    for var in github_vars:
        value = os.environ.get(var, 'Not set')
        print(f"  {var}: {value}")

def check_schedule_condition():
    """Check if we're running on a scheduled event and what schedule it is"""
    event_name = os.environ.get('GITHUB_EVENT_NAME', '')
    
    print(f"\n📅 Event Information:")
    print(f"  Event name: {event_name}")
    
    if event_name == 'schedule':
        # Try to determine which schedule triggered this
        # This is harder to determine directly, but we can check the current date
        now = datetime.now()
        print(f"  Current date: {now.strftime('%Y-%m-%d')}")
        print(f"  Day of month: {now.day}")
        print(f"  Month: {now.month}")
        
        # Check which schedule this might be
        if now.day == 3:
            print("  → This appears to be the Library Updates schedule (3rd of month)")
        elif now.day in [28, 29] and now.month % 3 == 0:
            print("  → This appears to be the Quarterly Reports schedule")
        elif 11 <= now.day <= 15 and now.month % 3 == 0:
            print("  → This appears to be the Regional Reports schedule")
        else:
            print("  → Schedule doesn't match expected patterns")

def test_script_execution():
    """Test if scripts can be executed"""
    scripts = [
        "scripts/library_updates-monthly.py",
        "scripts/private_sector_expectations-monthly.py", 
        "scripts/quarterly_reports-quarter.py",
        "scripts/regional_reports-quarter.py"
    ]
    
    print(f"\n🧪 Script Execution Test:")
    for script in scripts:
        if Path(script).exists():
            print(f"  ✅ {script} exists")
            # Test if it's executable (syntax check)
            try:
                result = subprocess.run([sys.executable, '-m', 'py_compile', script], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"     ✅ Syntax is valid")
                else:
                    print(f"     ❌ Syntax error: {result.stderr}")
            except Exception as e:
                print(f"     ⚠️  Could not test syntax: {e}")
        else:
            print(f"  ❌ {script} not found")

def check_directories():
    """Check if required directories exist"""
    dirs = [
        "reports and files/banxico_library_updates",
        "reports and files/banxico_quarterly_reports",
        "reports and files/banxico_regional_reports", 
        "reports and files/private_sector_expectations"
    ]
    
    print(f"\n📁 Directory Check:")
    for dir_path in dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"  ✅ {dir_path} exists")
            print(f"     📊 Contains {len(list(path.glob('*')))} files")
        else:
            print(f"  ❌ {dir_path} does not exist")
            try:
                path.mkdir(parents=True, exist_ok=True)
                print(f"     ✅ Created directory")
            except Exception as e:
                print(f"     ❌ Failed to create: {e}")

def main():
    """Main debug function"""
    print("🔧 GitHub Actions Debug Script")
    print("=" * 60)
    
    print_env_info()
    check_schedule_condition()
    test_script_execution()
    check_directories()
    
    print("\n" + "=" * 60)
    print("✅ Debug information collected")

if __name__ == "__main__":
    main()
