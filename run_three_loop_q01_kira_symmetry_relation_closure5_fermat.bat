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

set "HELPER=examples\three_loop_q01_kira_symmetry_relation_closure5_fermat.py"
set "PROBE=examples\three_loop_q01_kira_symmetry_linear_relation_probe_wave5.py"
if not exist "%HELPER%" (
  echo ERROR: closure-wave-5 helper was not found.
  pause
  exit /b 1
)
if not exist "%PROBE%" (
  echo ERROR: wave-5 relation probe wrapper was not found.
  pause
  exit /b 1
)

".venv\Scripts\python.exe" "%HELPER%" generate
if errorlevel 1 (
  set "RC=%ERRORLEVEL%"
  echo.
  echo Q01 symmetry relation closure-wave-5 generation failed with error code %RC%.
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
echo QEDCalc Q01 symmetry relation closure-wave-5 Kira/Fermat
echo project: %PROJECT_WIN%
echo mode: final lower-sector closure target only; FireFly disabled
echo alt_dir: symmetry_relation_closure5_fermat
echo.

wsl.exe --cd "%PROJECT_WIN%" bash -lc "set -o pipefail; export FERMATPATH=$HOME/fermat/Ferl7/fer64; echo Fermat: $FERMATPATH; kira jobs_q01_symmetry_relation_closure5_fermat.yaml 2>&1 | tee q01_symmetry_relation_closure5_fermat.log"
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
  echo.
  echo Q01 symmetry relation closure-wave-5 Kira/Fermat failed with error code %RC%.
  pause
  exit /b %RC%
)

".venv\Scripts\python.exe" "%HELPER%" audit
if errorlevel 1 (
  set "RC=%ERRORLEVEL%"
  echo.
  echo Q01 symmetry relation closure-wave-5 audit failed with error code %RC%.
  pause
  exit /b %RC%
)

echo.
echo Re-running symmetry relation rank probe with Fermat closure waves 1+2+3+4+5...
".venv\Scripts\python.exe" "%PROBE%"
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (
  echo Q01 symmetry relation closure-wave-5 workflow PASS
) else (
  echo Q01 symmetry relation closure-wave-5 workflow FAIL with error code %RC%.
)
pause
exit /b %RC%
