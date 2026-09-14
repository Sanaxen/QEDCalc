@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"

if not exist ".venv\Scripts\python.exe" (
  echo ERROR: QEDCalc virtual environment was not found.
  echo Expected: %CD%\.venv\Scripts\python.exe
  pause
  exit /b 1
)

set "SCRIPT=examples\three_loop_q01_kira_master_partition_audit.py"
if not exist "%SCRIPT%" (
  echo ERROR: master-form partition audit script was not found.
  pause
  exit /b 1
)

".venv\Scripts\python.exe" "%SCRIPT%"
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (
  echo Q01 master-form partition audit PASS
) else (
  echo Q01 master-form partition audit FAIL with error code %RC%.
)
pause
exit /b %RC%
