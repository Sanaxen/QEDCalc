@echo off
setlocal EnableExtensions
cd /d "%~dp0"

if "%~1"=="" goto :usage
if "%~2"=="" goto :usage

set "FAMILY=%~1"
set "SEED=%~2"
set "SOLVER=%~3"
if "%SOLVER%"=="" set "SOLVER=ordinary"

if /I not "%SOLVER%"=="ordinary" if /I not "%SOLVER%"=="firefly" (
  echo ERROR: solver must be ordinary or firefly.
  exit /b 2
)

if not exist ".venv\Scripts\python.exe" (
  echo ERROR: .venv\Scripts\python.exe not found.
  exit /b 1
)

".venv\Scripts\python.exe" -m examples.three_loop_master_basis_pipeline --family "%FAMILY%" --seed "%SEED%" --solver "%SOLVER%" --prepare
if errorlevel 1 exit /b %ERRORLEVEL%

for /f "usebackq delims=" %%I in (`powershell.exe -NoProfile -Command "('%FAMILY%').ToLowerInvariant()"`) do set "FAMILY_LOWER=%%I"
set "SOLVER_SUFFIX="
if /I "%SOLVER%"=="firefly" set "SOLVER_SUFFIX=_firefly"
set "WIN_PROJECT=%CD%\output\kira_%FAMILY_LOWER%%SOLVER_SUFFIX%_%SEED%"

if not exist "%WIN_PROJECT%\jobs.yaml" (
  echo ERROR: generic Kira project was not generated.
  echo Expected: %WIN_PROJECT%
  exit /b 3
)

echo QEDCalc generic master-basis Kira run
echo family: %FAMILY%
echo seed: %SEED%
echo solver: %SOLVER%
echo Windows project: %WIN_PROJECT%

wsl.exe --cd "%WIN_PROJECT%" bash -lc "set -o pipefail; command -v kira >/dev/null 2>&1 || { echo 'ERROR: kira not found in WSL PATH'; exit 127; }; export FERMATPATH=$HOME/fermat/Ferl7/fer64; rm -rf results sectormappings tmp firefly_saves ff_save firefly_saves_alt pyred; echo FERMATPATH=$FERMATPATH; kira jobs.yaml 2>&1 | tee kira_%SOLVER%_%SEED%.log"
set "KIRA_ERR=%ERRORLEVEL%"
if not "%KIRA_ERR%"=="0" (
  echo ERROR: Kira exited with code %KIRA_ERR%.
  exit /b %KIRA_ERR%
)

".venv\Scripts\python.exe" -m examples.three_loop_master_basis_pipeline --family "%FAMILY%" --seed "%SEED%" --solver "%SOLVER%" --finalize
set "AUDIT_ERR=%ERRORLEVEL%"
if not "%AUDIT_ERR%"=="0" exit /b %AUDIT_ERR%

endlocal
exit /b 0

:usage
echo Usage: %~nx0 FAMILY SEED [ordinary^|firefly]
echo Example: %~nx0 Q05_full r9s3d0 firefly
exit /b 2
