@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment not found. Running setup_env.bat...
    call setup_env.bat
    if errorlevel 1 exit /b 1
)

".venv\Scripts\python.exe" -m examples.renormalization_process
if errorlevel 1 (
    echo.
    echo QEDCalc renormalization demo failed.
    pause
    exit /b 1
)

echo.
echo QEDCalc renormalization demo completed successfully.
pause
