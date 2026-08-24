@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment not found. Running setup_env.bat...
    call setup_env.bat
    if errorlevel 1 exit /b 1
)
".venv\Scripts\python.exe" -m examples.vacuum_polarization_2loop_trial
if errorlevel 1 (
    echo.
    echo QEDCalc vacuum-polarization demo failed.
    pause
    exit /b 1
)
echo.
echo Output written to output\vacuum_polarization_2loop_trial.md
pause
