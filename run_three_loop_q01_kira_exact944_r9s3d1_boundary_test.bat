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

set "HELPER=examples\three_loop_q01_kira_exact944_r9s3d1_boundary_test.py"
if not exist "%HELPER%" (
  echo ERROR: r9s3d1 boundary-test helper was not found.
  pause
  exit /b 1
)

".venv\Scripts\python.exe" "%HELPER%" generate
if errorlevel 1 (
  set "RC=%ERRORLEVEL%"
  echo.
  echo Q01 exact944 r9s3d1 boundary generation failed with error code %RC%.
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

wsl.exe bash -lc "test -x $HOME/fermat/Ferl7/fer64"
if errorlevel 1 (
  echo ERROR: Fermat executable was not found or is not executable at $HOME/fermat/Ferl7/fer64.
  pause
  exit /b 4
)

set "PROJECT_WIN=%CD%\output\kira_q01_full_demand_r9s3d0"

echo.
echo QEDCalc Q01 exact944 r9s3d1 seed-boundary test
echo project: %PROJECT_WIN%
echo mode: fresh ordinary Kira/Fermat reduction; FireFly disabled
echo enlarged seed: r=9 s=3 d=1
echo alt_dir: exact944_r9s3d1_fermat
echo.

wsl.exe --cd "%PROJECT_WIN%" bash -lc "set -o pipefail; export FERMATPATH=$HOME/fermat/Ferl7/fer64; echo Fermat: $FERMATPATH; kira jobs_q01_exact944_r9s3d1_boundary.yaml 2>&1 | tee q01_exact944_r9s3d1_boundary.log"
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
  echo.
  echo Q01 exact944 r9s3d1 Kira/Fermat run failed with error code %RC%.
  pause
  exit /b %RC%
)

".venv\Scripts\python.exe" "%HELPER%" audit
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (
  echo Q01 exact944 r9s3d1 seed-boundary workflow PASS
) else (
  echo Q01 exact944 r9s3d1 seed-boundary workflow FAIL with error code %RC%.
)
pause
exit /b %RC%
