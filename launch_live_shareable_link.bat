@echo off
title AutoShare Ledger - Live Public Shareable Link
echo =====================================================================
echo          AutoShare Ledger - Live Public Link Generator
echo =====================================================================
echo.
echo [1/2] Starting Web Application Server...
start /B python web_app.py
timeout /t 2 >nul

echo.
echo [2/2] Generating Live Public HTTPS Link via Tunnel...
echo ---------------------------------------------------------------------
echo Copy the HTTPS link that appears below and share it with anyone!
echo (Keep this window open while you want the link to stay active)
echo ---------------------------------------------------------------------
echo.
ssh -o StrictHostKeyChecking=no -R 80:localhost:8000 serveo.net
pause
