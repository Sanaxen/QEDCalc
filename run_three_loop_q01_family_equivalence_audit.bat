@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo ERROR: .venv\Scripts\python.exe not found.
  exit /b 1
)

".venv\Scripts\python.exe" -m examples.three_loop_q01_family_equivalence_audit
set ERR=%ERRORLEVEL%
if not "%ERR%"=="0" exit /b %ERR%

endlocal
