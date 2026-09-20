@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo ERROR: .venv\Scripts\python.exe not found.
  echo Run setup_env.bat first.
  exit /b 1
)

".venv\Scripts\python.exe" examples\three_loop_input_to_family_audit.py
exit /b %ERRORLEVEL%
