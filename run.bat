@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Himoya Bot ishga tushirilmoqda...
echo.
.venv\Scripts\python.exe main.py
pause
