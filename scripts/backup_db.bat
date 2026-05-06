@echo off
REM Avtomatik kunlik backup wrapper (Windows Task Scheduler uchun).
REM %~dp0 = bu .bat fayl joylashgan papka (scripts\). Ota papkasi — loyiha ildizi.

set "ROOT=%~dp0.."
cd /d "%ROOT%"
mkdir "%ROOT%\data\backups" 2>nul
".venv\Scripts\python.exe" "scripts\backup_db.py" >> "data\backups\backup.log" 2>&1
exit /b %ERRORLEVEL%
