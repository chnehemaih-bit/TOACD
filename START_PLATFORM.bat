@echo off
title Agentic AI Code Analysis Platform Launcher
cd /d "%~dp0"

echo ==============================================================
echo   Agentic AI C++ Code Analysis & Healing Platform v2.0
echo ==============================================================
echo.

:: Check if server is already running on port 8000
netstat -ano | findstr :8000 | findstr LISTENING >nul
if %errorlevel% neq 0 (
    echo [1/2] Starting Python server on port 8000...
    start /b python server.py
    timeout /t 2 /nobreak >nul
) else (
    echo [1/2] Server is already running on port 8000.
)

echo [2/2] Opening website in your web browser...
start "" "http://localhost:8000/?v=%RANDOM%"

echo.
echo ==============================================================
echo   SUCCESS! Website opened in browser.
echo   You can minimize or close this window.
echo ==============================================================
timeout /t 3 >nul
exit
