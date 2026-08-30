@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Virtual environment not found. Run setup_env.bat first.
  exit /b 1
)
".venv\Scripts\python.exe" -m examples.full_target_reconstruction_trial
endlocal
