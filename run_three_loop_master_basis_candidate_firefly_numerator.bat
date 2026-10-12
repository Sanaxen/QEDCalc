@echo off
setlocal EnableExtensions
cd /d "%~dp0"

if "%~1"=="" goto :usage
if "%~2"=="" goto :usage
if "%~3"=="" goto :usage
if "%~4"=="" goto :usage

set "FAMILY=%~1"
set "BASELINE=%~2"
set "SECTOR=%~3"
set "MAXS=%~4"
set "ORDERING=%~5"
if "%ORDERING%"=="" set "ORDERING=5"

if not exist ".venv\Scripts\python.exe" (
  echo ERROR: .venv\Scripts\python.exe not found.
  exit /b 1
)

".venv\Scripts\python.exe" -m examples.three_loop_master_basis_candidate_firefly_numerator ^
  --family "%FAMILY%" ^
  --baseline-seed "%BASELINE%" ^
  --sector "%SECTOR%" ^
  --max-s "%MAXS%" ^
  --prepare
if errorlevel 1 exit /b %ERRORLEVEL%

set "PROJECT_FILE=%TEMP%\qedcalc_firefly_numerator_%RANDOM%_%RANDOM%.txt"
".venv\Scripts\python.exe" -m examples.three_loop_master_basis_candidate_firefly_numerator ^
  --family "%FAMILY%" ^
  --baseline-seed "%BASELINE%" ^
  --sector "%SECTOR%" ^
  --max-s "%MAXS%" ^
  --print-project > "%PROJECT_FILE%"
set "LIST_ERR=%ERRORLEVEL%"
if not "%LIST_ERR%"=="0" (
  if exist "%PROJECT_FILE%" del /q "%PROJECT_FILE%" >nul 2>&1
  exit /b %LIST_ERR%
)
set /p WIN_PROJECT=<"%PROJECT_FILE%"
del /q "%PROJECT_FILE%" >nul 2>&1

if not exist "%WIN_PROJECT%\jobs.yaml" (
  echo ERROR: FireFly numerator Kira project not found:
  echo   %WIN_PROJECT%
  exit /b 3
)

echo.
echo QEDCalc FireFly fixed-sector numerator run
echo project: %WIN_PROJECT%
echo integral ordering: %ORDERING%
echo.

wsl.exe --cd "%WIN_PROJECT%" bash -lc "set -o pipefail; command -v kira >/dev/null 2>&1 || { echo 'ERROR: kira not found in WSL PATH'; exit 127; }; export FERMATPATH=$HOME/fermat/Ferl7/fer64; rm -rf results sectormappings tmp firefly_saves ff_save firefly_saves_alt pyred; echo FERMATPATH=$FERMATPATH; echo INTEGRAL_ORDERING=%ORDERING%; kira --integral_ordering=%ORDERING% jobs.yaml 2>&1 | tee kira_firefly_numerator_order%ORDERING%.log"
set "KIRA_ERR=%ERRORLEVEL%"
if not "%KIRA_ERR%"=="0" (
  echo ERROR: Kira exited with code %KIRA_ERR%.
  exit /b %KIRA_ERR%
)

".venv\Scripts\python.exe" -m examples.three_loop_master_basis_candidate_firefly_numerator ^
  --family "%FAMILY%" ^
  --baseline-seed "%BASELINE%" ^
  --sector "%SECTOR%" ^
  --max-s "%MAXS%" ^
  --finalize
exit /b %ERRORLEVEL%

:usage
echo Usage: %~nx0 FAMILY BASELINE_SEED SECTOR MAX_S [ORDERING]
echo Example: %~nx0 VP05_full r8s3d0 199 6 5
exit /b 2
