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

set "AUDIT_PY=examples\three_loop_q01_kira_910_exact_closure1_firefly_export_audit.py"
if not exist "%AUDIT_PY%" (
  echo ERROR: FireFly export/audit helper was not found.
  echo Expected: %CD%\%AUDIT_PY%
  pause
  exit /b 1
)

".venv\Scripts\python.exe" "%AUDIT_PY%" generate-export
if errorlevel 1 (
  set "RC=%ERRORLEVEL%"
  echo.
  echo Q01 exact944 closure-wave-1 FireFly export job generation failed with error code %RC%.
  pause
  exit /b %RC%
)

where wsl.exe >nul 2>&1
if errorlevel 1 (
  echo ERROR: wsl.exe was not found.
  pause
  exit /b 2
)

wsl.exe bash -lc "command -v kira >/dev/null 2>&1"
if errorlevel 1 (
  echo ERROR: kira was not found in the WSL PATH.
  pause
  exit /b 2
)

set "PROJECT_WIN=%CD%\output\kira_q01_full_demand_r9s3d0"
if not exist "%PROJECT_WIN%" (
  echo ERROR: Q01 Kira project was not found.
  echo Expected: %PROJECT_WIN%
  pause
  exit /b 2
)

if not exist "%PROJECT_WIN%\exact944closure1_firefly" (
  echo ERROR: completed FireFly alt_dir was not found.
  echo Expected: %PROJECT_WIN%\exact944closure1_firefly
  echo The expensive FireFly reduction will NOT be recomputed by this runner.
  pause
  exit /b 2
)

echo.
echo QEDCalc Q01 exact944 closure-wave-1 FireFly export + audit
echo project: %PROJECT_WIN%
echo alt_dir: exact944closure1_firefly
echo mode: existing FireFly artifacts only; no projected-trace or reduction recomputation
echo.

wsl.exe --cd "%PROJECT_WIN%" bash -lc "set -o pipefail; export FERMATPATH=$HOME/fermat/Ferl7/fer64; kira jobs_exact944_closure1_firefly_export.yaml 2>&1 | tee q01_exact944_closure1_firefly_export.log"
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
  echo.
  echo Q01 exact944 closure-wave-1 FireFly FORM export failed with error code %RC%.
  pause
  exit /b %RC%
)

".venv\Scripts\python.exe" "%AUDIT_PY%" audit
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (
  echo Q01 exact944 closure-wave-1 FireFly export audit PASS
) else (
  echo Q01 exact944 closure-wave-1 FireFly export audit FAIL with error code %RC%.
)
pause
exit /b %RC%
