@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

if "%~1"=="" goto :usage
if "%~2"=="" goto :usage
if "%~3"=="" goto :usage

set "FAMILY=%~1"
set "BASELINE_SEED=%~2"
set "TEST_SEED=%~3"

if not exist ".venv\Scripts\python.exe" (
  echo ERROR: .venv\Scripts\python.exe not found.
  exit /b 1
)

".venv\Scripts\python.exe" -m examples.three_loop_master_basis_candidate_sector_closure --family "%FAMILY%" --baseline-seed "%BASELINE_SEED%" --solver masters --seed "%TEST_SEED%" --prepare
if errorlevel 1 exit /b %ERRORLEVEL%

set "PROJECT_LIST=%TEMP%\qedcalc_candidate_sector_closure_%RANDOM%_%RANDOM%.txt"
".venv\Scripts\python.exe" -m examples.three_loop_master_basis_candidate_sector_closure --family "%FAMILY%" --baseline-seed "%BASELINE_SEED%" --solver masters --seed "%TEST_SEED%" --print-projects > "%PROJECT_LIST%"
set "LIST_ERR=%ERRORLEVEL%"
if not "%LIST_ERR%"=="0" (
  if exist "%PROJECT_LIST%" del /q "%PROJECT_LIST%" >nul 2>&1
  echo ERROR: failed to obtain sector-local project list.
  exit /b %LIST_ERR%
)

set "PROJECT_COUNT=0"
for /f "usebackq delims=" %%P in ("%PROJECT_LIST%") do (
  set /a PROJECT_COUNT+=1
  set "WIN_PROJECT=%%P"
  if not exist "!WIN_PROJECT!\jobs.yaml" (
    echo ERROR: sector-local Kira project was not generated.
    echo Expected: !WIN_PROJECT!
    if exist "%PROJECT_LIST%" del /q "%PROJECT_LIST%" >nul 2>&1
    exit /b 3
  )

  echo.
  echo [!PROJECT_COUNT!] Kira project: !WIN_PROJECT!
  wsl.exe --cd "!WIN_PROJECT!" bash -lc "set -o pipefail; command -v kira >/dev/null 2>&1 || { echo 'ERROR: kira not found in WSL PATH'; exit 127; }; export FERMATPATH=$HOME/fermat/Ferl7/fer64; rm -rf results sectormappings tmp firefly_saves ff_save firefly_saves_alt pyred; echo FERMATPATH=$FERMATPATH; kira jobs.yaml 2>&1 | tee kira_masters_candidate_sector_closure.log"
  set "KIRA_ERR=!ERRORLEVEL!"
  if not "!KIRA_ERR!"=="0" (
    echo ERROR: Kira exited with code !KIRA_ERR!.
    if exist "%PROJECT_LIST%" del /q "%PROJECT_LIST%" >nul 2>&1
    exit /b !KIRA_ERR!
  )
)

if exist "%PROJECT_LIST%" del /q "%PROJECT_LIST%" >nul 2>&1

echo Sector-local Kira projects executed: %PROJECT_COUNT%

".venv\Scripts\python.exe" -m examples.three_loop_master_basis_candidate_sector_closure --family "%FAMILY%" --baseline-seed "%BASELINE_SEED%" --solver masters --seed "%TEST_SEED%" --finalize
exit /b %ERRORLEVEL%

:usage
echo Usage: %~nx0 FAMILY BASELINE_SEED TEST_SEED
echo Example: %~nx0 VP05_full r8s3d0 r9s5d2
exit /b 2
