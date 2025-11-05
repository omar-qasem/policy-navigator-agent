#!/usr/bin/env python3
"""
Test script to diagnose file upload path issue
Run this on your Windows machine to see the exact problem
"""

import os
import sys

print("=" * 60)
print("File Upload Path Diagnosis Tool")
print("=" * 60)
print()

# Test 1: Check os.path.basename behavior
print("Test 1: os.path.basename() behavior")
print("-" * 60)

test_paths = [
    "CFR-2025-title2-vol1.pdf",
    "C:\\Users\\Omar\\CFR-2025-title2-vol1.pdf",
    "/tmp/CFR-2025-title2-vol1.pdf",
    "folder\\subfolder\\file.pdf",
]

for path in test_paths:
    basename = os.path.basename(path)
    result = os.path.join('/tmp', basename)
    print(f"Input:  {path}")
    print(f"Basename: {basename}")
    print(f"Result: {result}")
    print()

# Test 2: Check which app file exists
print("\nTest 2: Check which app files exist")
print("-" * 60)

app_files = [
    'demo/app_faiss.py',
    'demo/app_agent.py',
    'demo/app.py',
    'demo/test_app.py'
]

for app_file in app_files:
    exists = os.path.exists(app_file)
    status = "✓ EXISTS" if exists else "✗ NOT FOUND"
    print(f"{app_file}: {status}")
    
    if exists:
        # Check if it has the fix
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
            has_basename = 'os.path.basename' in content
            has_safe_filename = 'safe_filename' in content
            
            if has_basename and has_safe_filename:
                print(f"  → ✓ HAS FIX (basename + safe_filename)")
            elif has_basename:
                print(f"  → ⚠ HAS basename but missing safe_filename variable")
            else:
                print(f"  → ✗ MISSING FIX (no basename)")
print()

# Test 3: Show the exact line that should be in the code
print("\nTest 3: Expected code in upload function")
print("-" * 60)
print("The upload function should have these lines:")
print()
print("    safe_filename = os.path.basename(file.filename)")
print("    temp_path = os.path.join('/tmp', safe_filename)")
print()

# Test 4: Instructions
print("\nTest 4: Next Steps")
print("-" * 60)
print("1. Check which app file you're running (app_faiss.py recommended)")
print("2. Make sure you restarted the server after git pull")
print("3. If still failing, send me the output of this script")
print()
print("To check which process is running:")
print("  Windows: tasklist | findstr python")
print("  Linux/Mac: ps aux | grep python")
print()
print("=" * 60)
