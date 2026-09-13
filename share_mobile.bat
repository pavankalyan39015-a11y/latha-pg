@echo off
cd /d "%~dp0"
title PG Mobile Public Link
echo ===================================================
echo   Starting Cloudflare Tunnel for Mobile Access...
echo ===================================================
cloudflared.exe tunnel --url http://localhost:8000
pause
