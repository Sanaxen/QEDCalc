@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment not found. Running setup_env.bat...
    call setup_env.bat
    if errorlevel 1 exit /b 1
)
".venv\Scripts\python.exe" -m examples.crossed_ladder_2loop_trial
if errorlevel 1 (
    echo.
    echo Crossed-ladder trial failed.
    pause
    exit /b 1
)
echo.
echo Crossed-ladder trial completed.
pause
