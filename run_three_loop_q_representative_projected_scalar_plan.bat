@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo ERROR: .venv\Scripts\python.exe not found.
  exit /b 1
)

".venv\Scripts\python.exe" examples\three_loop_q_representative_projected_scalar_plan.py
if errorlevel 1 exit /b %errorlevel%

endlocal
