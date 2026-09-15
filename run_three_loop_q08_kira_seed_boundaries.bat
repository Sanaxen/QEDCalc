@echo off
setlocal EnableExtensions
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo ERROR: .venv\Scripts\python.exe not found.
  exit /b 1
)

if not exist "output\three_loop_integral_family_audit\q08_r7s3d0_masters.txt" (
  echo ERROR: Q08 r7s3d0 baseline master copy not found.
  echo Run run_three_loop_q08_kira_r7s3d0.bat first.
  exit /b 2
)

echo ============================================================
echo QEDCalc Q08 seed-boundary run: r8s3d0
echo ============================================================
".venv\Scripts\python.exe" -m examples.three_loop_q08_kira_seed_boundary_audit --seed r8s3d0 --prepare
if errorlevel 1 exit /b %ERRORLEVEL%
set "WIN_PROJECT=%CD%\output\kira_q08_full_r8s3d0"
wsl.exe --cd "%WIN_PROJECT%" bash -lc "set -o pipefail; command -v kira >/dev/null 2>&1 || { echo 'ERROR: kira not found in WSL PATH'; exit 127; }; export FERMATPATH=$HOME/fermat/Ferl7/fer64; echo FERMATPATH=$FERMATPATH; kira jobs.yaml 2>&1 | tee kira_r8s3d0.log"
set "KIRA_ERR=%ERRORLEVEL%"
if not "%KIRA_ERR%"=="0" (
  echo ERROR: Q08 r8s3d0 Kira exited with code %KIRA_ERR%.
  exit /b %KIRA_ERR%
)
".venv\Scripts\python.exe" -m examples.three_loop_q08_kira_seed_boundary_audit --seed r8s3d0 --finalize
if errorlevel 1 exit /b %ERRORLEVEL%

echo ============================================================
echo QEDCalc Q08 seed-boundary run: r7s4d0
echo ============================================================
".venv\Scripts\python.exe" -m examples.three_loop_q08_kira_seed_boundary_audit --seed r7s4d0 --prepare
if errorlevel 1 exit /b %ERRORLEVEL%
set "WIN_PROJECT=%CD%\output\kira_q08_full_r7s4d0"
wsl.exe --cd "%WIN_PROJECT%" bash -lc "set -o pipefail; command -v kira >/dev/null 2>&1 || { echo 'ERROR: kira not found in WSL PATH'; exit 127; }; export FERMATPATH=$HOME/fermat/Ferl7/fer64; echo FERMATPATH=$FERMATPATH; kira jobs.yaml 2>&1 | tee kira_r7s4d0.log"
set "KIRA_ERR=%ERRORLEVEL%"
if not "%KIRA_ERR%"=="0" (
  echo ERROR: Q08 r7s4d0 Kira exited with code %KIRA_ERR%.
  exit /b %KIRA_ERR%
)
".venv\Scripts\python.exe" -m examples.three_loop_q08_kira_seed_boundary_audit --seed r7s4d0 --finalize
if errorlevel 1 exit /b %ERRORLEVEL%

echo ============================================================
echo QEDCalc Q08 seed-boundary run: r7s3d1
echo ============================================================
".venv\Scripts\python.exe" -m examples.three_loop_q08_kira_seed_boundary_audit --seed r7s3d1 --prepare
if errorlevel 1 exit /b %ERRORLEVEL%
set "WIN_PROJECT=%CD%\output\kira_q08_full_r7s3d1"
wsl.exe --cd "%WIN_PROJECT%" bash -lc "set -o pipefail; command -v kira >/dev/null 2>&1 || { echo 'ERROR: kira not found in WSL PATH'; exit 127; }; export FERMATPATH=$HOME/fermat/Ferl7/fer64; echo FERMATPATH=$FERMATPATH; kira jobs.yaml 2>&1 | tee kira_r7s3d1.log"
set "KIRA_ERR=%ERRORLEVEL%"
if not "%KIRA_ERR%"=="0" (
  echo ERROR: Q08 r7s3d1 Kira exited with code %KIRA_ERR%.
  exit /b %KIRA_ERR%
)
".venv\Scripts\python.exe" -m examples.three_loop_q08_kira_seed_boundary_audit --seed r7s3d1 --finalize
if errorlevel 1 exit /b %ERRORLEVEL%

echo ============================================================
echo QEDCalc Q08 aggregate seed-boundary audit
echo ============================================================
".venv\Scripts\python.exe" -m examples.three_loop_q08_kira_seed_boundary_audit --aggregate
set "AUDIT_ERR=%ERRORLEVEL%"
if not "%AUDIT_ERR%"=="0" exit /b %AUDIT_ERR%

endlocal
