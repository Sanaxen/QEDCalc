@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo QEDCalc virtual environment not found.
  echo Run setup_env.bat first.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m examples.laporta_closure_trial
if errorlevel 1 (
  echo.
  echo Laporta closure demo failed.
  pause
  exit /b 1
)
echo.
echo Laporta closure demo completed.
pause
