@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "PYTHONPATH=%CD%"

if not exist ".venv\Scripts\python.exe" (
  echo ERROR: .venv\Scripts\python.exe not found.
  exit /b 1
)

if not exist "output\three_loop_integral_family_audit\q02_firefly_r8s3d0_masters.txt" (
  echo ERROR: Q02 FireFly baseline master copy was not found.
  echo Run run_three_loop_q02_kira_firefly_r8s3d0.bat first.
  exit /b 2
)

for %%S in (r9s3d0 r8s4d0 r8s3d1) do call :run_seed %%S
if errorlevel 1 exit /b %ERRORLEVEL%

".venv\Scripts\python.exe" -m examples.three_loop_q02_kira_firefly_seed_boundary_audit --aggregate
set "AUDIT_ERR=%ERRORLEVEL%"
if not "%AUDIT_ERR%"=="0" exit /b %AUDIT_ERR%

echo.
echo QEDCalc Q02 FireFly seed-boundary workflow PASS
endlocal
exit /b 0

:run_seed
set "SEED=%~1"
".venv\Scripts\python.exe" -m examples.three_loop_q02_kira_firefly_seed_boundary_audit --seed %SEED% --prepare
if errorlevel 1 exit /b %ERRORLEVEL%

set "WIN_PROJECT=%CD%\output\kira_q02_full_firefly_%SEED%"
if not exist "%WIN_PROJECT%" (
  echo ERROR: Q02 FireFly boundary project was not found.
  echo Expected: %WIN_PROJECT%
  exit /b 2
)

echo.
echo QEDCalc Q02 %SEED% Kira + FireFly boundary run
echo Windows project: %WIN_PROJECT%
echo mode: fresh full reduction with FireFly
echo.

wsl.exe --cd "%WIN_PROJECT%" bash -lc "set -o pipefail; command -v kira >/dev/null 2>&1 || { echo 'ERROR: kira not found in WSL PATH'; exit 127; }; echo Cleaning stale Kira/FireFly state...; rm -rf results sectormappings tmp firefly_saves ff_save firefly_saves_alt pyred; export FERMATPATH=$HOME/fermat/Ferl7/fer64; echo FERMATPATH=$FERMATPATH; kira jobs.yaml 2>&1 | tee kira_firefly_%SEED%.log"
set "KIRA_ERR=%ERRORLEVEL%"
if not "%KIRA_ERR%"=="0" (
  echo ERROR: Kira/FireFly %SEED% exited with code %KIRA_ERR%.
  exit /b %KIRA_ERR%
)

".venv\Scripts\python.exe" -m examples.three_loop_q02_kira_firefly_seed_boundary_audit --seed %SEED% --finalize
set "AUDIT_ERR=%ERRORLEVEL%"
if not "%AUDIT_ERR%"=="0" exit /b %AUDIT_ERR%

exit /b 0
