@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

if "%~1"=="" goto :usage
if "%~2"=="" goto :usage

set "FAMILY=%~1"
set "BASELINE_SEED=%~2"
set "SOLVER=%~3"
if "%SOLVER%"=="" set "SOLVER=firefly"

if /I not "%SOLVER%"=="ordinary" if /I not "%SOLVER%"=="firefly" (
  echo ERROR: solver must be ordinary or firefly.
  exit /b 2
)

if not exist ".venv\Scripts\python.exe" (
  echo ERROR: .venv\Scripts\python.exe not found.
  exit /b 1
)

".venv\Scripts\python.exe" -m examples.three_loop_master_basis_candidate_closure --family "%FAMILY%" --baseline-seed "%BASELINE_SEED%" --solver "%SOLVER%" --prepare
if errorlevel 1 exit /b %ERRORLEVEL%

echo.
echo QEDCalc generic candidate master closure Kira runs
echo family: %FAMILY%
echo baseline seed: %BASELINE_SEED%
echo solver: %SOLVER%
echo.
echo Rough runtime guide ^(heuristic only^):
echo   3 sequential Kira/FireFly boundary runs
echo   typical per boundary : about 10-90 minutes
echo   typical total        : about 30 minutes-4.5 hours
echo   difficult seeds may take longer; overnight execution is reasonable
echo   this is not a completion-time guarantee
echo.

rem Avoid nested FOR /F command quoting around .venv\Scripts\python.exe.
rem Write the three project paths to a temporary file first, then iterate it.
set "PROJECT_LIST=%TEMP%\qedcalc_candidate_closure_%RANDOM%_%RANDOM%.txt"
".venv\Scripts\python.exe" -m examples.three_loop_master_basis_candidate_closure --family "%FAMILY%" --baseline-seed "%BASELINE_SEED%" --solver "%SOLVER%" --print-projects > "%PROJECT_LIST%"
set "LIST_ERR=%ERRORLEVEL%"
if not "%LIST_ERR%"=="0" (
  if exist "%PROJECT_LIST%" del /q "%PROJECT_LIST%" >nul 2>&1
  echo ERROR: failed to obtain candidate-closure project list.
  exit /b %LIST_ERR%
)

set "PROJECT_COUNT=0"
for /f "usebackq delims=" %%P in ("%PROJECT_LIST%") do (
  set /a PROJECT_COUNT+=1
  set "WIN_PROJECT=%%P"
  if not exist "!WIN_PROJECT!\jobs.yaml" (
    echo ERROR: candidate-closure Kira project was not generated.
    echo Expected: !WIN_PROJECT!
    if exist "%PROJECT_LIST%" del /q "%PROJECT_LIST%" >nul 2>&1
    exit /b 3
  )
  if not exist "!WIN_PROJECT!\mandatory_candidate_closure_targets.txt" (
    echo ERROR: candidate-closure mandatory list was not generated.
    echo Expected: !WIN_PROJECT!\mandatory_candidate_closure_targets.txt
    if exist "%PROJECT_LIST%" del /q "%PROJECT_LIST%" >nul 2>&1
    exit /b 4
  )

  echo.
  echo [!PROJECT_COUNT!/3] Kira project: !WIN_PROJECT!
  wsl.exe --cd "!WIN_PROJECT!" bash -lc "set -o pipefail; command -v kira >/dev/null 2>&1 || { echo 'ERROR: kira not found in WSL PATH'; exit 127; }; export FERMATPATH=$HOME/fermat/Ferl7/fer64; rm -rf results sectormappings tmp firefly_saves ff_save firefly_saves_alt pyred; echo FERMATPATH=$FERMATPATH; kira jobs.yaml 2>&1 | tee kira_%SOLVER%_candidate_closure.log"
  set "KIRA_ERR=!ERRORLEVEL!"
  if not "!KIRA_ERR!"=="0" (
    echo ERROR: Kira exited with code !KIRA_ERR!.
    if exist "%PROJECT_LIST%" del /q "%PROJECT_LIST%" >nul 2>&1
    exit /b !KIRA_ERR!
  )
)

if exist "%PROJECT_LIST%" del /q "%PROJECT_LIST%" >nul 2>&1

if not "%PROJECT_COUNT%"=="3" (
  echo ERROR: expected exactly 3 candidate-closure projects, got %PROJECT_COUNT%.
  exit /b 5
)

".venv\Scripts\python.exe" -m examples.three_loop_master_basis_candidate_closure --family "%FAMILY%" --baseline-seed "%BASELINE_SEED%" --solver "%SOLVER%" --finalize
set "AUDIT_ERR=%ERRORLEVEL%"
if not "%AUDIT_ERR%"=="0" exit /b %AUDIT_ERR%

endlocal
exit /b 0

:usage
echo Usage: %~nx0 FAMILY BASELINE_SEED [ordinary^|firefly]
echo Example: %~nx0 Q05_full r8s3d0 firefly
exit /b 2
