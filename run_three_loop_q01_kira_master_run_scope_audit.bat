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

set "HELPER=examples\three_loop_q01_kira_master_run_scope_audit.py"
if not exist "%HELPER%" (
  echo ERROR: Q01 master run-scope audit helper was not found.
  pause
  exit /b 1
)

echo.
echo QEDCalc Q01 masters.final run-scope audit
echo mode: saved provenance artifact only; no Kira/FireFly/Fermat/projected-trace recomputation
echo.

".venv\Scripts\python.exe" "%HELPER%"
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (
  echo Q01 masters.final run-scope audit PASS
) else (
  echo Q01 masters.final run-scope audit FAIL with error code %RC%.
)
pause
exit /b %RC%
