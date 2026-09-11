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

echo QEDCalc Q01 exact944 unresolved-leaf sector diagnostic
echo mode: saved artifacts only; no Kira rerun
echo.

".venv\Scripts\python.exe" examples\three_loop_q01_kira_910_exact_leaf_diagnostic.py
set "RC=%ERRORLEVEL%"

if "%RC%"=="0" (
  echo.
  echo Q01 exact944 unresolved-leaf sector diagnostic PASS
) else (
  echo.
  echo Q01 exact944 unresolved-leaf sector diagnostic failed with error code %RC%.
)
pause
exit /b %RC%
