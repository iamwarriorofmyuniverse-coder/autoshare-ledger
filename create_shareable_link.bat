@echo off
title AutoShare Ledger - Instant Shareable Public Link
echo =================================================================
echo       AutoShare Ledger - Shareable Public Link Generator
echo =================================================================
echo.
echo [1/2] Starting AutoShare Ledger Web App Server in background...
start /B python web_app.py

timeout /t 2 >nul

echo.
echo [2/2] Generating Instant Live Public HTTPS Link...
echo -----------------------------------------------------------------
echo Share the HTTPS link generated below with your teacher/friends:
echo -----------------------------------------------------------------
echo.
ssh -p 443 -R0:localhost:8000 a.pinggy.io
pause
