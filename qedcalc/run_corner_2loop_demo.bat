@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment not found. Running setup_env.bat first...
    call setup_env.bat
    if errorlevel 1 exit /b 1
)

set "PYTHONPATH=%CD%"
".venv\Scripts\python.exe" -m examples.corner_2loop_trial
if errorlevel 1 (
    echo.
    echo QEDCalc corner two-loop demo failed.
    pause
    exit /b 1
)

echo.
echo Output written to output\corner_2loop_trial.md
pause
endlocal
