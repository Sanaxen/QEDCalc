@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo QEDCalc virtual environment not found. Run setup_env.bat first.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m examples.phase10_basis_evaluation_trial
if errorlevel 1 (
  echo Phase-10 basis evaluation failed.
  pause
  exit /b 1
)
echo.
echo Phase-10 basis evaluation completed.
pause
