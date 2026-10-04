@echo off
title AutoShare Ledger - Web Link Server
echo =======================================================
echo    AutoShare Ledger - Web Application Server
echo    DBMS Laboratory Project (Regulation 2023)
echo =======================================================
echo.
echo Starting Local Web Server at http://127.0.0.1:8000 ...
start http://127.0.0.1:8000
python web_app.py
pause
