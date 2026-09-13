@echo off
cd /d "%~dp0"
title PG Management Server
echo ===================================================
echo   Starting Latha PG Management System...
echo ===================================================
venv\Scripts\python.exe run.py
pause
