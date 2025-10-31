# Troubleshooting Guide - Policy Navigator Agent

This guide helps resolve common issues with the Policy Navigator Agent.

---

## Issue: "Failed to fetch" Error on File Upload/URL Scraping

### Problem
When trying to upload files or scrape URLs, you get an error: "Error: Failed to fetch"

### Root Cause
This is typically a CORS (Cross-Origin Resource Sharing) issue or the Flask server not responding properly.

### Solution

#### Step 1: Install flask-cors
```bash
pip3 install flask-cors
```

#### Step 2: Verify CORS is enabled in app.py
Check that these lines are present in `demo/app.py`:

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS
```

#### Step 3: Restart the Flask server
```bash
# Kill existing Flask process
pkill -f "python3 app.py"

# Start fresh
cd demo
python3 app.py
```

#### Step 4: Test with curl
```bash
# Test file upload
echo "Test content" > /tmp/test.txt
curl -X POST -F "file=@/tmp/test.txt" http://localhost:5000/api/upload

# Test URL scraping
curl -X POST -H "Content-Type: application/json" \
  -d '{"url":"https://www.epa.gov"}' \
  http://localhost:5000/api/scrape
```

---

## Issue: Flask Server Won't Start

### Problem
Running `python3 app.py` fails or the server doesn't start.

### Solutions

#### Check Port Availability
```bash
# See what's using port 5000
lsof -i :5000

# Kill the process if needed
lsof -ti:5000 | xargs kill -9
```

#### Use a Different Port
```bash
PORT=5001 python3 app.py
```

#### Check for Missing Dependencies
```bash
pip3 install -r requirements.txt
```

#### Verify Environment Variables
```bash
# Check .env file exists
cat .env

# Should contain:
# AIXPLAIN_API_KEY=your_key_here
```

---

## Issue: Vector Database Not Found

### Problem
Error: "No such file or directory: 'chroma_db'"

### Solution
```bash
# Run data ingestion to create the database
cd /home/ubuntu/policy-navigator-agent
python3 src/data/ingest_data.py --reset
```

---

## Issue: aiXplain Agents Not Working

### Problem
Queries return errors or agents can't be loaded.

### Solutions

#### Check Agent IDs
```bash
# Verify agent_ids.json exists
cat agent_ids.json
```

#### Recreate Agents
```bash
python3 src/agents/build_agents.py
```

#### Check API Key
```bash
# Test API key
python3 -c "
from dotenv import load_dotenv
import os
load_dotenv()
print(os.getenv('AIXPLAIN_API_KEY'))
"
```

---

## Issue: Document Upload Fails

### Problem
Files upload but aren't processed correctly.

### Solutions

#### Check File Format
Supported formats: XML, TXT

```bash
# Verify file type
file your_document.xml
```

#### Check File Size
Maximum size: 16MB

```bash
# Check file size
ls -lh your_document.xml
```

#### Check Permissions
```bash
# Ensure upload directory is writable
mkdir -p /tmp/policy_uploads
chmod 777 /tmp/policy_uploads
```

---

## Issue: URL Scraping Fails

### Problem
URL scraping returns errors or no content.

### Solutions

#### Verify URL is Accessible
```bash
curl -I https://www.epa.gov
```

#### Check for Government Domain
The scraper prioritizes .gov domains. Non-government sites may have limited support.

#### Test Scraper Directly
```bash
python3 -c "
from src.tools.url_scraper_tool import URLScraperTool
scraper = URLScraperTool()
result = scraper.scrape_url('https://www.epa.gov')
print(result)
"
```

---

## Issue: Queries Return No Results

### Problem
Searches return "No results found" even for valid queries.

### Solutions

#### Check Database Status
```bash
python3 -c "
from src.data.vector_store import VectorStore
vs = VectorStore(persist_directory='chroma_db')
stats = vs.get_collection_stats()
print(f'Total documents: {stats[\"total_documents\"]}')
"
```

#### Re-index Data
```bash
python3 src/data/ingest_data.py --reset
```

#### Try Different Query Phrasing
- Instead of: "air quality"
- Try: "EPA air quality standards" or "40 CFR air quality"

---

## Issue: Federal Register API Not Working

### Problem
Federal Register queries return errors.

### Solution

#### Test API Directly
```bash
curl "https://www.federalregister.gov/api/v1/documents.json?per_page=1"
```

#### Check Tool Implementation
```bash
python3 -c "
from src.tools.federal_register_tool import FederalRegisterTool
fr = FederalRegisterTool()
results = fr.search_documents('EPA', per_page=5)
print(f'Found {len(results)} documents')
"
```

---

## Debug Mode

### Enable Detailed Logging

Edit `demo/app.py` and add:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Flask Logs

```bash
# If running in background
tail -f /tmp/flask_app.log

# If running in foreground, logs appear in terminal
```

### Test Individual Components

```bash
# Test document processor
python3 src/tools/document_processor.py

# Test vector store
python3 src/data/vector_store.py

# Test Federal Register tool
python3 src/tools/federal_register_tool.py

# Test URL scraper
python3 src/tools/url_scraper_tool.py
```

---

## Common Error Messages

### "AIXPLAIN_API_KEY not found"
**Solution:** Create `.env` file with your API key

### "Port 5000 is in use"
**Solution:** Use a different port: `PORT=5001 python3 app.py`

### "No module named 'flask_cors'"
**Solution:** `pip3 install flask-cors`

### "No such file or directory: 'chroma_db'"
**Solution:** Run `python3 src/data/ingest_data.py --reset`

### "Failed to connect to localhost:5000"
**Solution:** Make sure Flask is running: `python3 demo/app.py`

---

## Getting Help

If you're still experiencing issues:

1. **Check the logs:** Look for error messages in the Flask output
2. **Test components individually:** Use the debug commands above
3. **Review documentation:** See README.md and SETUP_GUIDE.md
4. **Open an issue:** https://github.com/omar-qasem/policy-navigator-agent/issues

Include in your issue report:
- Error message (full traceback)
- Steps to reproduce
- Your environment (OS, Python version)
- Relevant log files

---

## Quick Fix Checklist

- [ ] `.env` file exists with valid API key
- [ ] `flask-cors` is installed
- [ ] `chroma_db` directory exists (run ingestion if not)
- [ ] Flask server is running
- [ ] Port 5000 (or chosen port) is available
- [ ] All dependencies installed: `pip3 install -r requirements.txt`
- [ ] Python 3.10+ is being used

---

**Last Updated:** October 31, 2025
