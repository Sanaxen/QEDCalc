@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo [ERROR] Virtual environment not found. Run setup_env.bat first.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m examples.phase5_depth2_master_candidate_trial
if errorlevel 1 (
  echo [ERROR] Demo failed.
  pause
  exit /b 1
)
echo [OK] Phase-5 depth-2 master-candidate audit completed.
pause
