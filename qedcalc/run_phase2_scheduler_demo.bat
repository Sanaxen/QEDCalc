@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo QEDCalc virtual environment was not found.
  echo Run setup_env.bat first.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m examples.phase2_neighborhood_scheduler_trial
if errorlevel 1 (
  echo.
  echo Phase-2 scheduler demo failed.
  pause
  exit /b 1
)
echo.
echo Phase-2 scheduler demo completed.
pause
