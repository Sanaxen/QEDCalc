@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"

if not exist ".venv\Scripts\python.exe" (
  echo ERROR: QEDCalc virtual environment was not found.
  pause
  exit /b 1
)

where wsl.exe >nul 2>&1
if errorlevel 1 (
  echo ERROR: wsl.exe was not found.
  pause
  exit /b 2
)

wsl.exe bash -lc "test -x $HOME/fermat/Ferl7/fer64"
if errorlevel 1 (
  echo ERROR: Fermat executable was not found or is not executable at $HOME/fermat/Ferl7/fer64.
  pause
  exit /b 4
)

echo.
echo QEDCalc Q01 reusable master-coefficient API validation
echo mode: saved artifacts only; no projected trace or Kira/FireFly run
echo.

".venv\Scripts\python.exe" "examples\three_loop_q01_master_coefficient_api_validation.py"
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (
  echo Q01 reusable master-coefficient API validation PASS
) else (
  echo Q01 reusable master-coefficient API validation FAIL with error code %RC%.
)
pause
exit /b %RC%
