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

set "HELPER=examples\three_loop_q01_kira_symmetry_closure_export.py"
if not exist "%HELPER%" (
  echo ERROR: Q01 symmetry-expansion closure export helper was not found.
  echo Expected: %CD%\%HELPER%
  pause
  exit /b 1
)

where wsl.exe >nul 2>&1
if errorlevel 1 (
  echo ERROR: wsl.exe was not found.
  pause
  exit /b 1
)

".venv\Scripts\python.exe" "%HELPER%" generate
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" goto :done

set "PROJECT_WIN=%CD%\output\kira_q01_full_demand_r9s3d0"

wsl.exe --cd "%PROJECT_WIN%" bash -lc "set -o pipefail; export FERMATPATH=$HOME/fermat/Ferl7/fer64; kira jobs_q01_symmetry_closure_firefly_export.yaml 2>&1 | tee q01_symmetry_closure_firefly_export.log"
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" goto :done

".venv\Scripts\python.exe" "%HELPER%" audit
set "RC=%ERRORLEVEL%"

:done
echo.
if "%RC%"=="0" (
  echo Q01 symmetry-expansion closure export audit PASS
) else if "%RC%"=="3" (
  echo Q01 symmetry-expansion closure export audit INCOMPLETE; another saved-result export wave may be needed.
) else (
  echo Q01 symmetry-expansion closure export audit FAIL with error code %RC%.
)
pause
exit /b %RC%
