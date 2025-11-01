@echo off
echo ============================================================
echo Policy Navigator Agent - Windows Launcher
echo ============================================================
echo.

REM Activate virtual environment
echo [1/3] Activating virtual environment...
call ..\venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Could not activate virtual environment
    echo Please make sure you created the venv: python -m venv venv
    pause
    exit /b 1
)

REM Check if flask-cors is installed
echo [2/3] Checking dependencies...
pip show flask-cors >nul 2>&1
if errorlevel 1 (
    echo Installing flask-cors...
    pip install flask-cors
)

REM Start Flask
echo [3/3] Starting Flask server...
echo.
echo ============================================================
echo Server will start on http://localhost:5001
echo Keep this window open!
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

python start_server.py

pause
