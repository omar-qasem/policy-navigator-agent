"""
Startup script with comprehensive error checking
"""

import sys
import os

print("="*60)
print("Policy Navigator Agent - Startup Diagnostics")
print("="*60)
print()

# Check Python version
print(f"✓ Python version: {sys.version}")
print()

# Check current directory
print(f"✓ Current directory: {os.getcwd()}")
print()

# Check if .env exists
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(env_path):
    print(f"✓ .env file found")
else:
    print(f"✗ .env file NOT found")
    print("  Creating .env file...")
    with open(env_path, 'w') as f:
        f.write("AIXPLAIN_API_KEY=ada6267c2fbef32d4178f00df6462c7b1558d161790894ce51725f62309b3aa3\n")
    print("  ✓ .env file created")

print()

# Check required packages
print("Checking required packages...")
required_packages = {
    'flask': 'Flask',
    'flask_cors': 'flask-cors',
    'aixplain': 'aixplain',
    'chromadb': 'chromadb',
    'bs4': 'beautifulsoup4',
    'requests': 'requests',
    'dotenv': 'python-dotenv'
}

missing = []
for module, package in required_packages.items():
    try:
        __import__(module)
        print(f"  ✓ {package}")
    except ImportError:
        print(f"  ✗ {package} - NOT INSTALLED")
        missing.append(package)

print()

if missing:
    print("⚠ Missing packages detected!")
    print(f"Run: pip install {' '.join(missing)}")
    print()
    sys.exit(1)

# Check vector database
chroma_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'chroma_db')
if os.path.exists(chroma_path):
    print(f"✓ Vector database found")
else:
    print(f"⚠ Vector database NOT found")
    print("  The app will still run, but you should run: python src\\data\\ingest_data.py --reset")

print()

# Try to import app components
print("Testing app imports...")
try:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from demo.app import app
    print("  ✓ App imported successfully")
except Exception as e:
    print(f"  ✗ Error importing app: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("="*60)
print("All checks passed! Starting server...")
print("="*60)
print()

# Start the server
if __name__ == '__main__':
    try:
        port = 5001
        print(f"Server starting on http://localhost:{port}")
        print(f"Press Ctrl+C to stop")
        print()
        app.run(host='0.0.0.0', port=port, debug=True)
    except Exception as e:
        print(f"\n✗ Error starting server: {str(e)}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
