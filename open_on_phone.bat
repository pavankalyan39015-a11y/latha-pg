@echo off
cd /d "%~dp0"
title Latha PG Manager - Phone Launcher
echo ===================================================
echo   Starting Latha PG Manager for Phone...
echo ===================================================
venv\Scripts\python.exe launch_mobile.py
pause
