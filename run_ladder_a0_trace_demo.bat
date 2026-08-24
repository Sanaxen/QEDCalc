@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment not found. Running setup_env.bat...
    call setup_env.bat
    if errorlevel 1 exit /b 1
)
".venv\Scripts\python.exe" -m examples.ladder_a0_raw_trace_trial
if errorlevel 1 (
    echo.
    echo Ladder A0 raw trace trial failed.
    pause
    exit /b 1
)
echo.
echo Output: output\ladder_A0_raw_trace_trial.md
pause
