@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo ERROR: .venv\Scripts\python.exe not found.
  exit /b 1
)
.venv\Scripts\python.exe -m examples.three_loop_q03_existing_family_reuse_audit
exit /b %errorlevel%
