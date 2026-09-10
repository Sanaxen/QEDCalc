@echo off
setlocal
cd /d "%~dp0"

set "PYTHONPATH=%CD%"

if not exist ".venv\Scripts\python.exe" (
  echo ERROR: QEDCalc virtual environment was not found.
  echo Expected: %CD%\.venv\Scripts\python.exe
  pause
  exit /b 1
)

".venv\Scripts\python.exe" examples\three_loop_q01_kira_910_demand_plan.py
set "RC=%ERRORLEVEL%"

echo.
if not "%RC%"=="0" echo Q01 Kira 910 demand planner failed with error code %RC%.
pause
exit /b %RC%
