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

set "AUDIT=examples\three_loop_q01_kira_symmetry_relation_final_audit.py"
if not exist "%AUDIT%" (
  echo ERROR: final symmetry relation audit helper was not found.
  pause
  exit /b 1
)

echo QEDCalc Q01 symmetry relation final saved-artifact audit
echo mode: no Kira, FireFly, Fermat, or projected-trace recomputation
echo.

".venv\Scripts\python.exe" "%AUDIT%"
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (
  echo Q01 symmetry relation final audit PASS
) else (
  echo Q01 symmetry relation final audit FAIL with error code %RC%.
)
pause
exit /b %RC%
