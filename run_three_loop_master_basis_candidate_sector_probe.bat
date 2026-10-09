@echo off
setlocal EnableExtensions
cd /d "%~dp0"

if "%~1"=="" goto :usage
if "%~2"=="" goto :usage
if "%~3"=="" goto :usage
if "%~4"=="" goto :usage
if "%~5"=="" goto :usage

set "FAMILY=%~1"
set "BASELINE_SEED=%~2"
set "TEST_SEED=%~3"
set "SECTOR=%~4"
set "ORDERING=%~5"

set "PROJECT=output\kira_%FAMILY:_full=%_masters_candidate_sector_closure_%BASELINE_SEED%_%TEST_SEED%_sec%SECTOR%"

rem Existing project names are lowercase family ids; resolve VP05_full explicitly
if /I "%FAMILY%"=="VP05_full" set "PROJECT=output\kira_vp05_full_masters_candidate_sector_closure_%BASELINE_SEED%_%TEST_SEED%_sec%SECTOR%"

if not exist "%PROJECT%\jobs.yaml" (
  echo ERROR: prepared sector-local Kira project not found:
  echo   %PROJECT%
  echo Run the normal sector-local closure prepare/run at least once first.
  exit /b 3
)

echo QEDCalc candidate sector probe
echo family: %FAMILY%
echo baseline seed: %BASELINE_SEED%
echo test seed: %TEST_SEED%
echo sector: %SECTOR%
echo integral ordering: %ORDERING%
echo project: %PROJECT%
echo.
echo This probe cleans only this sector project's runtime outputs.
echo Other completed sector-local projects are preserved.
echo.

wsl.exe --cd "%CD%\%PROJECT%" bash -lc "set -o pipefail; command -v kira >/dev/null 2>&1 || { echo 'ERROR: kira not found in WSL PATH'; exit 127; }; export FERMATPATH=$HOME/fermat/Ferl7/fer64; rm -rf results sectormappings tmp firefly_saves ff_save firefly_saves_alt pyred; echo FERMATPATH=$FERMATPATH; echo INTEGRAL_ORDERING=%ORDERING%; kira --integral_ordering=%ORDERING% jobs.yaml 2>&1 | tee kira_masters_candidate_sector_probe_order%ORDERING%.log"
set "KIRA_ERR=%ERRORLEVEL%"
if not "%KIRA_ERR%"=="0" (
  echo ERROR: Kira probe exited with code %KIRA_ERR%.
  exit /b %KIRA_ERR%
)

echo.
echo QEDCalc candidate sector probe PASS
exit /b 0

:usage
echo Usage: %~nx0 FAMILY BASELINE_SEED TEST_SEED SECTOR ORDERING
echo Example: %~nx0 VP05_full r8s3d0 r8s6d2 199 5
exit /b 2
