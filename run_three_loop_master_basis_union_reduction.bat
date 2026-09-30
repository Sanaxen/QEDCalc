@echo off
setlocal EnableExtensions
cd /d "%~dp0"

if "%~1"=="" goto :usage
if "%~2"=="" goto :usage

set "FAMILY=%~1"
set "BASELINE_SEED=%~2"
set "SOLVER=%~3"
set "MODE=%~4"
if "%SOLVER%"=="" set "SOLVER=firefly"
set "PREPARE_EXTRA="
if /I "%MODE%"=="fresh" set "PREPARE_EXTRA=--fresh"

if /I not "%SOLVER%"=="ordinary" if /I not "%SOLVER%"=="firefly" (
  echo ERROR: solver must be ordinary or firefly.
  exit /b 2
)

if not exist ".venv\Scripts\python.exe" (
  echo ERROR: .venv\Scripts\python.exe not found.
  exit /b 1
)

".venv\Scripts\python.exe" -m examples.three_loop_master_basis_union_reduction --family "%FAMILY%" --baseline-seed "%BASELINE_SEED%" --solver "%SOLVER%" --prepare %PREPARE_EXTRA%
if errorlevel 1 exit /b %ERRORLEVEL%

for /f "usebackq delims=" %%I in (`powershell.exe -NoProfile -Command "('%FAMILY%').ToLowerInvariant()"`) do set "FAMILY_LOWER=%%I"
set "WIN_PROJECT=%CD%\output\kira_%FAMILY_LOWER%_%SOLVER%_union_%BASELINE_SEED%"

if not exist "%WIN_PROJECT%\jobs.yaml" (
  echo ERROR: generic mandatory-union Kira project was not generated.
  echo Expected: %WIN_PROJECT%
  exit /b 3
)
if not exist "%WIN_PROJECT%\mandatory_union_targets.txt" (
  echo ERROR: mandatory union target copy was not generated.
  echo Expected: %WIN_PROJECT%\mandatory_union_targets.txt
  exit /b 4
)

echo QEDCalc generic mandatory-union Kira run
echo family: %FAMILY%
echo baseline seed: %BASELINE_SEED%
echo solver: %SOLVER%
echo Windows project: %WIN_PROJECT%

wsl.exe --cd "%WIN_PROJECT%" bash -lc "set -o pipefail; command -v kira >/dev/null 2>&1 || { echo 'ERROR: kira not found in WSL PATH'; exit 127; }; export FERMATPATH=$HOME/fermat/Ferl7/fer64; echo FERMATPATH=$FERMATPATH; echo QEDCalc runtime mode: %MODE%; kira jobs.yaml 2>&1 | tee -a kira_%SOLVER%_union_%BASELINE_SEED%.log"
set "KIRA_ERR=%ERRORLEVEL%"
if not "%KIRA_ERR%"=="0" (
  echo ERROR: Kira exited with code %KIRA_ERR%.
  exit /b %KIRA_ERR%
)

".venv\Scripts\python.exe" -m examples.three_loop_master_basis_union_reduction --family "%FAMILY%" --baseline-seed "%BASELINE_SEED%" --solver "%SOLVER%" --finalize
set "AUDIT_ERR=%ERRORLEVEL%"
if not "%AUDIT_ERR%"=="0" exit /b %AUDIT_ERR%

endlocal
exit /b 0

:usage
echo Usage: %~nx0 FAMILY BASELINE_SEED [ordinary^|firefly] [fresh]
echo Default mode preserves compatible interrupted Kira/FireFly runtime state.
echo Example resume-safe: %~nx0 Q05_full r8s3d0 firefly
echo Example fresh      : %~nx0 Q05_full r8s3d0 firefly fresh
exit /b 2
