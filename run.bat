@echo off
title BIOPRESS Analytics Server
echo ========================================================
echo   BIOPRESS Analytics - Starting Web Application
echo ========================================================
cd /d "%~dp0backend"

set "PYTHON_EXE=C:\Users\zeina\AppData\Local\Programs\Python\Python311\python.exe"

if exist "%PYTHON_EXE%" (
    echo [INFO] Using installed Python at: %PYTHON_EXE%
    echo [INFO] Dashboard URL: http://127.0.0.1:8000
    echo [INFO] Press Ctrl+C to stop the server
    echo ========================================================
    "%PYTHON_EXE%" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
) else (
    echo [INFO] Falling back to system python...
    python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
)
pause
