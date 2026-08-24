@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo [QEDCalc] .venv not found. Run setup_env.bat first.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m examples.rational_reconstruction_trial
if errorlevel 1 (
  echo.
  echo [QEDCalc] Rational reconstruction demo failed.
  pause
  exit /b 1
)
echo.
echo [QEDCalc] Rational reconstruction demo completed.
pause
