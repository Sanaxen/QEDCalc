@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo QEDCalc virtual environment not found. Run setup_env.bat first.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m examples.phase4_local_master_candidate_trial
if errorlevel 1 (
  echo Phase-4 master-candidate demo failed.
  pause
  exit /b 1
)
echo.
echo Output: output\phase4_local_master_candidate_trial.md
pause
