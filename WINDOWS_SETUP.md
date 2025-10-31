# Windows Setup Guide - Policy Navigator Agent

This guide provides Windows-specific instructions for running the Policy Navigator Agent.

---

## Quick Start for Windows

### 1. Pull Latest Changes

```cmd
cd C:\Users\HP\policy-navigator-agent
git pull origin master
```

### 2. Install Dependencies

```cmd
pip install flask-cors
```

Or install all dependencies:

```cmd
pip install -r requirements.txt
```

### 3. Stop Existing Flask Server

**Option A: Find and Kill Process**
```cmd
netstat -ano | findstr :5000
taskkill /PID <PID_NUMBER> /F
```

Replace `<PID_NUMBER>` with the actual process ID from the first command.

**Option B: Close Command Prompt**
Simply close the Command Prompt window running Flask and open a new one.

### 4. Start Flask Server

```cmd
cd demo
python app.py
```

---

## Detailed Windows Commands

### Check if Port 5000 is in Use

```cmd
netstat -ano | findstr :5000
```

Output example:
```
TCP    0.0.0.0:5000    0.0.0.0:0    LISTENING    12345
```

The last number (12345) is the Process ID (PID).

### Kill Process by PID

```cmd
taskkill /PID 12345 /F
```

### Kill All Python Processes (Use with Caution!)

```cmd
taskkill /IM python.exe /F
```

### Use a Different Port

```cmd
set PORT=5001
python app.py
```

Or in one line:
```cmd
python app.py --port 5001
```

---

## Fix the "Failed to fetch" Error on Windows

### Step 1: Verify flask-cors is Installed

```cmd
pip show flask-cors
```

If not installed:
```cmd
pip install flask-cors
```

### Step 2: Verify .env File

```cmd
type .env
```

Should show:
```
AIXPLAIN_API_KEY=ada6267c2fbef32d4178f00df6462c7b1558d161790894ce51725f62309b3aa3
```

If file doesn't exist, create it:
```cmd
echo AIXPLAIN_API_KEY=ada6267c2fbef32d4178f00df6462c7b1558d161790894ce51725f62309b3aa3 > .env
```

### Step 3: Restart Flask

1. **Stop Flask:** Press `Ctrl+C` in the Command Prompt running Flask
2. **Start Flask:**
   ```cmd
   cd demo
   python app.py
   ```

### Step 4: Test in Browser

Open your browser and go to:
```
http://localhost:5000
```

Try uploading a file or scraping a URL.

---

## Common Windows Issues

### Issue: "python: command not found"

**Solution:** Use `python` instead of `python3`

```cmd
python app.py
```

### Issue: "pip: command not found"

**Solution:** Use `python -m pip`

```cmd
python -m pip install flask-cors
```

### Issue: "Permission denied" when killing process

**Solution:** Run Command Prompt as Administrator

1. Search for "cmd" in Start Menu
2. Right-click "Command Prompt"
3. Select "Run as administrator"
4. Run the taskkill command again

### Issue: Port 5000 already in use

**Solution 1: Kill the process**
```cmd
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**Solution 2: Use a different port**
```cmd
set PORT=5001
cd demo
python app.py
```

### Issue: Virtual environment not activated

**Solution:**
```cmd
cd C:\Users\HP\policy-navigator-agent
venv\Scripts\activate
```

You should see `(venv)` in your prompt.

---

## Complete Setup from Scratch (Windows)

### 1. Clone Repository

```cmd
cd C:\Users\HP
git clone https://github.com/omar-qasem/policy-navigator-agent.git
cd policy-navigator-agent
```

### 2. Create Virtual Environment

```cmd
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```cmd
pip install -r requirements.txt
```

### 4. Create .env File

```cmd
echo AIXPLAIN_API_KEY=ada6267c2fbef32d4178f00df6462c7b1558d161790894ce51725f62309b3aa3 > .env
```

### 5. Ingest Data

```cmd
python src\data\ingest_data.py --reset
```

### 6. Run Demo

```cmd
cd demo
python app.py
```

### 7. Open Browser

Navigate to: http://localhost:5000

---

## Running in Background (Windows)

### Option 1: Use `start` command

```cmd
cd demo
start /B python app.py > flask.log 2>&1
```

### Option 2: Use PowerShell

```powershell
cd demo
Start-Process python -ArgumentList "app.py" -WindowStyle Hidden
```

### Option 3: Use Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., "At startup")
4. Action: Start a program
5. Program: `C:\Users\HP\policy-navigator-agent\venv\Scripts\python.exe`
6. Arguments: `app.py`
7. Start in: `C:\Users\HP\policy-navigator-agent\demo`

---

## Testing Upload and Scrape Features

### Test File Upload (Windows)

```cmd
echo Test policy content > test.txt
curl -X POST -F "file=@test.txt" http://localhost:5000/api/upload
```

If `curl` is not available, use PowerShell:

```powershell
$file = "test.txt"
$url = "http://localhost:5000/api/upload"
$filePath = (Get-Item $file).FullName
$form = @{
    file = Get-Item -Path $filePath
}
Invoke-RestMethod -Uri $url -Method Post -Form $form
```

### Test URL Scraping (Windows)

```cmd
curl -X POST -H "Content-Type: application/json" -d "{\"url\":\"https://www.epa.gov\"}" http://localhost:5000/api/scrape
```

Or use PowerShell:

```powershell
$body = @{
    url = "https://www.epa.gov"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/scrape" -Method Post -Body $body -ContentType "application/json"
```

---

## Firewall Settings

If you can't access the server from another device on your network:

1. Open Windows Defender Firewall
2. Click "Advanced settings"
3. Click "Inbound Rules" → "New Rule"
4. Select "Port" → Next
5. Select "TCP" and enter port "5000"
6. Select "Allow the connection"
7. Apply to all profiles
8. Name it "Flask Policy Navigator"

---

## Environment Variables (Windows)

### Set Temporarily (Current Session)

```cmd
set AIXPLAIN_API_KEY=ada6267c2fbef32d4178f00df6462c7b1558d161790894ce51725f62309b3aa3
set PORT=5000
set DEBUG=True
```

### Set Permanently (System-wide)

```cmd
setx AIXPLAIN_API_KEY "ada6267c2fbef32d4178f00df6462c7b1558d161790894ce51725f62309b3aa3"
```

**Note:** Permanent variables require restarting Command Prompt.

---

## Troubleshooting on Windows

### Check Python Version

```cmd
python --version
```

Should be Python 3.10 or higher.

### Check Installed Packages

```cmd
pip list
```

Verify these are installed:
- aixplain
- beautifulsoup4
- chromadb
- Flask
- flask-cors
- python-dotenv
- requests

### Check if Flask is Running

```cmd
netstat -ano | findstr :5000
```

### View Flask Logs

If running in background with log file:
```cmd
type flask.log
```

Or use PowerShell:
```powershell
Get-Content flask.log -Wait
```

---

## Quick Fix Commands (Copy-Paste)

**Stop Flask and Restart:**
```cmd
taskkill /F /IM python.exe
cd C:\Users\HP\policy-navigator-agent\demo
python app.py
```

**Install Missing Dependencies:**
```cmd
pip install flask-cors python-dotenv
```

**Verify Everything is Working:**
```cmd
curl http://localhost:5000/health
```

Should return: `{"status":"healthy","timestamp":"..."}`

---

## Getting Help

If issues persist:

1. Check TROUBLESHOOTING.md for general issues
2. Review Flask output for error messages
3. Ensure virtual environment is activated: `(venv)` in prompt
4. Verify all dependencies are installed: `pip list`
5. Open an issue: https://github.com/omar-qasem/policy-navigator-agent/issues

---

**Last Updated:** October 31, 2025  
**Tested on:** Windows 10/11
