@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "PYTHONPATH=%CD%"

if not exist ".venv\Scripts\python.exe" (
  echo ERROR: .venv\Scripts\python.exe not found.
  exit /b 1
)

".venv\Scripts\python.exe" -m examples.three_loop_q02_kira_firefly_r8s3d0_audit --prepare
if errorlevel 1 exit /b %ERRORLEVEL%

set "WIN_PROJECT=%CD%\output\kira_q02_full_firefly_r8s3d0"
if not exist "%WIN_PROJECT%" (
  echo ERROR: Q02 FireFly Kira project was not found.
  echo Expected: %WIN_PROJECT%
  exit /b 2
)

echo.
echo QEDCalc Q02 r8s3d0 Kira + FireFly baseline run
echo Windows project: %WIN_PROJECT%
echo mode: fresh full reduction with FireFly
echo note: ordinary Q02 Kira/Fermat partial run is not reused
echo.

wsl.exe --cd "%WIN_PROJECT%" bash -lc "set -o pipefail; command -v kira >/dev/null 2>&1 || { echo 'ERROR: kira not found in WSL PATH'; exit 127; }; echo Cleaning stale Kira/FireFly state...; rm -rf results sectormappings tmp firefly_saves ff_save firefly_saves_alt pyred; export FERMATPATH=$HOME/fermat/Ferl7/fer64; echo FERMATPATH=$FERMATPATH; kira jobs.yaml 2>&1 | tee kira_firefly_r8s3d0.log"
set "KIRA_ERR=%ERRORLEVEL%"
if not "%KIRA_ERR%"=="0" (
  echo ERROR: Kira/FireFly exited with code %KIRA_ERR%.
  exit /b %KIRA_ERR%
)

".venv\Scripts\python.exe" -m examples.three_loop_q02_kira_firefly_r8s3d0_audit --finalize
set "AUDIT_ERR=%ERRORLEVEL%"
if not "%AUDIT_ERR%"=="0" exit /b %AUDIT_ERR%

endlocal
