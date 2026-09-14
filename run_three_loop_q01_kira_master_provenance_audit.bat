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

set "SCRIPT=examples\three_loop_q01_kira_master_provenance_audit.py"
if not exist "%SCRIPT%" (
  echo ERROR: Q01 master provenance audit script was not found.
  pause
  exit /b 1
)

echo.
echo QEDCalc Q01 Kira master provenance audit
echo mode: saved artifacts only; no Kira/FireFly/Fermat/projected-trace recomputation
echo.

".venv\Scripts\python.exe" "%SCRIPT%"
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (
  echo Q01 Kira master provenance audit PASS
) else (
  echo Q01 Kira master provenance audit FAIL with error code %RC%.
)
pause
exit /b %RC%
