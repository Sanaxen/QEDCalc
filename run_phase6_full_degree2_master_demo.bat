@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Virtual environment not found. Run setup_env.bat first.
  exit /b 1
)
".venv\Scripts\python.exe" -m examples.phase6_full_degree2_master_candidate_trial
if errorlevel 1 exit /b 1
echo.
echo Output: output\phase6_full_degree2_master_candidate_trial.md
endlocal
