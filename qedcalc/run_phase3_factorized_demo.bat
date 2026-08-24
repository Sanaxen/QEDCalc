@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo QEDCalc virtual environment was not found.
  echo Run setup_env.bat first.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m examples.phase3_factorized_subtopology_trial
if errorlevel 1 (
  echo.
  echo Phase-3 factorized-subtopology demo failed.
  pause
  exit /b 1
)
echo.
echo Phase-3 factorized-subtopology demo completed.
pause
