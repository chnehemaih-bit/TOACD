@echo off
title Agentic AI Code Analysis Platform v2.0
cd /d "C:\Users\sanjay\Downloads\AI Based synatx error classification"
echo ==============================================================
echo   Agentic AI Code Analysis Platform v2.0
echo   Compiler Design * Security * Green Computing * Repair
echo ==============================================================
echo.
echo [CHECK] Verifying Python dependencies...
python -c "import http.server, json, re, os, sys; print('  Core modules OK')"
echo.
echo [START] Launching server on http://localhost:8000
echo [INFO]  Press Ctrl+C in this window to stop the server.
echo.
start "" http://localhost:8000
python server.py
pause
