@echo off
setlocal EnableExtensions
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo ERROR: .venv\Scripts\python.exe not found.
  exit /b 1
)

".venv\Scripts\python.exe" -m examples.three_loop_q02_firefly_master_union_audit
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" exit /b %RC%

endlocal
