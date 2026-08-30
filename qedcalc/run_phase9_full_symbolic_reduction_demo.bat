@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo [ERROR] Virtual environment not found. Run setup_env.bat first.
  exit /b 1
)
".venv\Scripts\python.exe" -m examples.phase9_full_symbolic_reduction_trial
if errorlevel 1 exit /b %errorlevel%
echo.
echo [OK] See output\phase9_full_symbolic_reduction_trial.md
endlocal
