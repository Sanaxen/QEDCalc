@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [INFO] Virtual environment is not installed yet.
    call setup_env.bat
    if errorlevel 1 exit /b 1
)

".venv\Scripts\python.exe" -m pytest -q
pause
