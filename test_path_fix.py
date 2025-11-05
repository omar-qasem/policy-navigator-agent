#!/usr/bin/env python3
"""
Test script to diagnose file upload path issue
Run this on your Windows machine to see the exact problem
"""

import os
import sys
import tempfile

print("=" * 60)
print("File Upload Path Diagnosis Tool v2")
print("=" * 60)
print()

# Test 1: Check tempfile.gettempdir()
print("Test 1: tempfile.gettempdir() behavior")
print("-" * 60)
temp_dir = tempfile.gettempdir()
print(f"System temp directory: {temp_dir}")
print(f"Type: {type(temp_dir)}")
print()

# Test 2: Check path joining with tempfile
print("Test 2: Path joining with tempfile.gettempdir()")
print("-" * 60)

test_filenames = [
    "CFR-2025-title2-vol1.pdf",
    "test.xml",
    "document.txt",
]

for filename in test_filenames:
    safe_filename = os.path.basename(filename)
    temp_path = os.path.join(temp_dir, safe_filename)
    print(f"Filename: {filename}")
    print(f"Basename: {safe_filename}")
    print(f"Full path: {temp_path}")
    print(f"Path exists: {os.path.exists(os.path.dirname(temp_path))}")
    print()

# Test 3: Verify the fix is in place
print("Test 3: Check which app files have the fix")
print("-" * 60)

app_files = [
    'demo/app_faiss.py',
    'demo/app_agent.py',
    'demo/app.py',
    'demo/test_app.py'
]

for app_file in app_files:
    if not os.path.exists(app_file):
        print(f"{app_file}: ✗ NOT FOUND")
        continue
        
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    has_tempfile_import = 'import tempfile' in content
    has_gettempdir = 'tempfile.gettempdir()' in content
    has_hardcoded_tmp = "'/tmp'" in content or '"/tmp"' in content
    
    print(f"{app_file}:")
    print(f"  ✓ import tempfile: {'YES' if has_tempfile_import else 'NO'}")
    print(f"  ✓ tempfile.gettempdir(): {'YES' if has_gettempdir else 'NO'}")
    print(f"  ✗ hardcoded /tmp: {'YES (BAD!)' if has_hardcoded_tmp else 'NO (GOOD!)'}")
    
    if has_tempfile_import and has_gettempdir and not has_hardcoded_tmp:
        print(f"  → ✅ FULLY FIXED")
    elif has_hardcoded_tmp:
        print(f"  → ❌ STILL HAS HARDCODED /tmp")
    else:
        print(f"  → ⚠ PARTIALLY FIXED")
    print()

# Test 4: Show expected code
print("Test 4: Expected code in upload function")
print("-" * 60)
print("The upload function should have:")
print()
print("    import tempfile  # at the top")
print()
print("    safe_filename = os.path.basename(file.filename)")
print("    temp_dir = tempfile.gettempdir()")
print("    temp_path = os.path.join(temp_dir, safe_filename)")
print()

# Test 5: Instructions
print("Test 5: Next Steps")
print("-" * 60)
print("1. Run: git pull origin master")
print("2. Restart your Flask server")
print("3. Try uploading a file")
print()
print("If it still fails, the issue is somewhere else.")
print("Send me the FULL error message from the browser console.")
print()
print("=" * 60)
