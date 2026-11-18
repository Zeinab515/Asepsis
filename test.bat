@echo off
title BIOPRESS Analytics Test Suite
echo ========================================================
echo   BIOPRESS Analytics - Running Test Suite (pytest)
echo ========================================================
cd /d "%~dp0backend"

set "PYTHON_EXE=C:\Users\zeina\AppData\Local\Programs\Python\Python311\python.exe"

if exist "%PYTHON_EXE%" (
    "%PYTHON_EXE%" -m pytest -v
) else (
    python -m pytest -v
)
pause
