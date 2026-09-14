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

set "HELPER=examples\three_loop_q01_kira_exact944_seed_boundary_complete_audit.py"
if not exist "%HELPER%" (
  echo ERROR: combined seed-boundary audit helper was not found.
  echo Expected: %CD%\%HELPER%
  pause
  exit /b 1
)

echo.
echo QEDCalc Q01 exact944 combined seed-boundary audit
echo This is a cheap saved-artifact audit; Kira is not rerun.
echo.

".venv\Scripts\python.exe" "%HELPER%"
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (
  echo Q01 exact944 combined seed-boundary audit PASS
) else (
  echo Q01 exact944 combined seed-boundary audit FAIL with error code %RC%.
)
pause
exit /b %RC%
