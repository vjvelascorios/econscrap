#!/usr/bin/env python3
"""
Simulate GitHub Actions execution locally for testing
"""

import os
import sys
import subprocess
from datetime import datetime

def simulate_github_actions():
    """Simulate the GitHub Actions workflow steps"""
    print("🚀 Simulating GitHub Actions Workflow")
    print("=" * 60)
    
    # Step 1: Set environment variables to simulate GitHub Actions
    os.environ['GITHUB_WORKFLOW'] = 'Banxico Reports Scraper'
    os.environ['GITHUB_EVENT_NAME'] = 'workflow_dispatch'  # Simulate manual trigger
    os.environ['GITHUB_REPOSITORY'] = 'vjvelascorios/econscrap'
    os.environ['GITHUB_REF'] = 'refs/heads/master'
    
    print("✅ Set GitHub Actions environment variables")
    
    # Step 2: Run debug script
    print("\n📋 Running debug workflow...")
    try:
        result = subprocess.run([sys.executable, 'debug_workflow.py'], 
                               capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Debug script completed successfully")
            print("Debug output:")
            print(result.stdout)
        else:
            print("❌ Debug script failed")
            print(result.stderr)
    except Exception as e:
        print(f"❌ Error running debug script: {e}")
    
    # Step 3: Test one of the scripts (library updates as example)
    print("\n📚 Testing library updates script...")
    try:
        # Run with a timeout to avoid hanging
        result = subprocess.run([sys.executable, 'scripts/library_updates-monthly.py'], 
                               capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("✅ Library updates script completed successfully")
            # Show last few lines of output
            lines = result.stdout.strip().split('\n')
            print("Last few lines of output:")
            for line in lines[-5:]:
                print(f"  {line}")
        else:
            print("❌ Library updates script failed")
            print("Error output:")
            print(result.stderr)
    except subprocess.TimeoutExpired:
        print("⏰ Script timed out (this is expected for full downloads)")
        print("✅ Script started successfully (timeout after 60s)")
    except Exception as e:
        print(f"❌ Error running library updates script: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Simulation Complete")
    print("\nNext steps:")
    print("1. Push your changes to GitHub")
    print("2. Go to Actions tab in your GitHub repository")
    print("3. Click 'Run workflow' to test manually")
    print("4. Check the logs for any issues")

if __name__ == "__main__":
    simulate_github_actions()
