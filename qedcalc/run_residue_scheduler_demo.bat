@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo [ERROR] .venv was not found. Run setup_env.bat first.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m examples.residue_scheduler_trial
if errorlevel 1 (
  echo [ERROR] Residue scheduler demo failed.
  pause
  exit /b 1
)
echo [OK] Residue scheduler demo completed.
pause
