@echo off
setlocal EnableExtensions
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo ERROR: .venv\Scripts\python.exe not found.
  exit /b 1
)
if not exist "output\three_loop_integral_family_audit\q10_r7s3d0_masters.txt" (
  echo ERROR: Q10 r7s3d0 baseline master copy not found.
  echo Run run_three_loop_q10_kira_r7s3d0.bat first.
  exit /b 2
)

for %%S in (r8s3d0 r7s4d0 r7s3d1) do call :run_seed %%S
if errorlevel 1 exit /b %ERRORLEVEL%

".venv\Scripts\python.exe" -m examples.three_loop_q10_kira_seed_boundary_audit --aggregate
if errorlevel 1 exit /b %ERRORLEVEL%
endlocal
exit /b 0

:run_seed
set "SEED=%~1"
echo ============================================================
echo QEDCalc Q10 seed-boundary run: %SEED%
echo ============================================================
".venv\Scripts\python.exe" -m examples.three_loop_q10_kira_seed_boundary_audit --seed %SEED% --prepare
if errorlevel 1 exit /b %ERRORLEVEL%
set "WIN_PROJECT=%CD%\output\kira_q10_full_%SEED%"
wsl.exe --cd "%WIN_PROJECT%" bash -lc "set -o pipefail; command -v kira >/dev/null 2>&1 || { echo 'ERROR: kira not found in WSL PATH'; exit 127; }; export FERMATPATH=$HOME/fermat/Ferl7/fer64; echo FERMATPATH=$FERMATPATH; kira jobs.yaml 2>&1 | tee kira_%SEED%.log"
set "KIRA_ERR=%ERRORLEVEL%"
if not "%KIRA_ERR%"=="0" exit /b %KIRA_ERR%
".venv\Scripts\python.exe" -m examples.three_loop_q10_kira_seed_boundary_audit --seed %SEED% --finalize
if errorlevel 1 exit /b %ERRORLEVEL%
exit /b 0
