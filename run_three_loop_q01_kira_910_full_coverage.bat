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

echo QEDCalc Q01 full-demand Kira 910-integral coverage audit
echo mode: saved artifacts only; no Kira rerun
echo.

".venv\Scripts\python.exe" examples\three_loop_q01_kira_910_full_coverage.py
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (
  echo Q01 full-demand Kira 910-integral coverage PASS
) else (
  echo Q01 full-demand Kira 910-integral coverage failed with error code %RC%.
)
pause
exit /b %RC%
