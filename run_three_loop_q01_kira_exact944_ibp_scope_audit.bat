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

set "SCRIPT=examples\three_loop_q01_kira_exact944_ibp_scope_audit.py"
if not exist "%SCRIPT%" (
  echo ERROR: exact944 IBP scope audit script was not found.
  pause
  exit /b 1
)

echo QEDCalc Q01 exact944 IBP/reduction-scope audit
echo mode: saved artifacts only; no Kira/FireFly/Fermat/projected-trace recomputation
echo.

".venv\Scripts\python.exe" "%SCRIPT%"
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (
  echo Q01 exact944 IBP/reduction-scope audit PASS
) else (
  echo Q01 exact944 IBP/reduction-scope audit FAIL with error code %RC%.
)
pause
exit /b %RC%
