@echo off
setlocal EnableExtensions
cd /d "%~dp0"

if "%~1"=="" goto :usage

if not exist ".venv\Scripts\python.exe" (
  echo ERROR: .venv\Scripts\python.exe not found.
  exit /b 1
)

".venv\Scripts\python.exe" -m examples.three_loop_firefly_resume_audit --family "%~1"
set "ERR=%ERRORLEVEL%"
endlocal
exit /b %ERR%

:usage
echo Usage: %~nx0 FAMILY
echo Example: %~nx0 Q03_full
exit /b 2
