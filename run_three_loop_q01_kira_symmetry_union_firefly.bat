@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"

if not exist ".venv\Scripts\python.exe" (
  echo ERROR: QEDCalc virtual environment was not found.
  pause
  exit /b 1
)

set "HELPER=examples\three_loop_q01_kira_symmetry_union_firefly.py"
".venv\Scripts\python.exe" "%HELPER%" generate
if errorlevel 1 (
  set "RC=%ERRORLEVEL%"
  echo Q01 closure1+symmetry FireFly generation failed with error code %RC%.
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
  echo ERROR: Fermat executable was not found.
  pause
  exit /b 4
)

set "PROJECT_WIN=%CD%\output\kira_q01_full_demand_r9s3d0"

echo.
echo QEDCalc Q01 closure-wave-1 plus symmetry Kira FireFly
echo project: %PROJECT_WIN%
echo mode: validated closure-wave-1 target set plus symmetry gaps
echo alt_dir: exact944closure1_plus_symmetry_firefly
echo NOTE: exact944closure1_firefly is not modified.
echo.

wsl.exe --cd "%PROJECT_WIN%" bash -lc "set -o pipefail; export FERMATPATH=$HOME/fermat/Ferl7/fer64; kira --bunch_size=1 jobs_q01_exact944_closure1_plus_symmetry_firefly.yaml 2>&1 | tee q01_exact944_closure1_plus_symmetry_firefly.log"
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
  echo.
  echo Q01 closure1+symmetry Kira FireFly failed with error code %RC%.
  pause
  exit /b %RC%
)

wsl.exe --cd "%PROJECT_WIN%" bash -lc "set -o pipefail; export FERMATPATH=$HOME/fermat/Ferl7/fer64; kira jobs_q01_symmetry_union_firefly_export.yaml 2>&1 | tee q01_symmetry_union_firefly_export.log"
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
  echo.
  echo Q01 symmetry union kira2form export failed with error code %RC%.
  pause
  exit /b %RC%
)

".venv\Scripts\python.exe" "%HELPER%" audit
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (
  echo Q01 closure1+symmetry FireFly PASS
) else (
  echo Q01 closure1+symmetry FireFly audit FAIL with error code %RC%.
)
pause
exit /b %RC%
