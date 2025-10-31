"""
Diagnostic script to check if everything is set up correctly
"""

import sys
import os

print("="*60)
print("Policy Navigator Agent - Diagnostic Tool")
print("="*60)
print()

# Check Python version
print("✓ Python version:", sys.version)
print()

# Check current directory
print("✓ Current directory:", os.getcwd())
print()

# Check if .env exists
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(env_path):
    print("✓ .env file found at:", env_path)
else:
    print("✗ .env file NOT found at:", env_path)
print()

# Check required packages
print("Checking required packages...")
required_packages = [
    'flask',
    'flask_cors',
    'aixplain',
    'chromadb',
    'beautifulsoup4',
    'requests',
    'dotenv'
]

missing_packages = []
for package in required_packages:
    try:
        __import__(package)
        print(f"  ✓ {package}")
    except ImportError:
        print(f"  ✗ {package} - NOT INSTALLED")
        missing_packages.append(package)

print()

if missing_packages:
    print("⚠ Missing packages detected!")
    print("Run this command to install them:")
    print(f"  pip install {' '.join(missing_packages)}")
    print()
else:
    print("✓ All required packages are installed!")
    print()

# Check if chroma_db exists
chroma_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'chroma_db')
if os.path.exists(chroma_path):
    print("✓ Vector database found at:", chroma_path)
else:
    print("✗ Vector database NOT found at:", chroma_path)
    print("  Run this command to create it:")
    print("  python src\\data\\ingest_data.py --reset")

print()

# Try to load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(env_path)
    api_key = os.getenv('AIXPLAIN_API_KEY')
    if api_key:
        print("✓ API key loaded successfully")
        print(f"  Key starts with: {api_key[:10]}...")
    else:
        print("✗ API key not found in .env file")
except Exception as e:
    print("✗ Error loading .env file:", str(e))

print()
print("="*60)
print("Diagnostic complete!")
print("="*60)

input("\nPress Enter to exit...")
