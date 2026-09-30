@echo off
setlocal EnableExtensions
cd /d "%~dp0"

if "%~1"=="" goto :usage
set "FAMILY=%~1"
set "LEVEL=%~2"
set "MODE=%~3"
if "%LEVEL%"=="" set "LEVEL=1"
set "FRESH_ARG="
if /I "%MODE%"=="fresh" set "FRESH_ARG=--fresh"

if not exist ".venv\Scripts\python.exe" (
  echo ERROR: .venv\Scripts\python.exe not found.
  exit /b 1
)

".venv\Scripts\python.exe" -m examples.three_loop_master_basis_sparse_discovery --family "%FAMILY%" --level "%LEVEL%" --prepare %FRESH_ARG%
if errorlevel 1 exit /b %ERRORLEVEL%

for /f "usebackq delims=" %%I in (`powershell.exe -NoProfile -Command "('%FAMILY%').ToLowerInvariant()"`) do set "FAMILY_LOWER=%%I"
set "WIN_PROJECT=%CD%\output\kira_%FAMILY_LOWER%_firefly_sparse_l%LEVEL%"

if not exist "%WIN_PROJECT%\jobs.yaml" (
  echo ERROR: sparse Kira project was not generated.
  echo Expected: %WIN_PROJECT%
  exit /b 3
)

echo QEDCalc sparse FireFly master discovery
echo family: %FAMILY%
echo level: %LEVEL%
echo Windows project: %WIN_PROJECT%

wsl.exe --cd "%WIN_PROJECT%" bash -lc "set -o pipefail; command -v kira >/dev/null 2>&1 || { echo 'ERROR: kira not found in WSL PATH'; exit 127; }; export FERMATPATH=$HOME/fermat/Ferl7/fer64; echo FERMATPATH=$FERMATPATH; kira jobs.yaml 2>&1 | tee -a kira_firefly_sparse_l%LEVEL%.log"
set "KIRA_ERR=%ERRORLEVEL%"
if not "%KIRA_ERR%"=="0" (
  echo ERROR: Kira exited with code %KIRA_ERR%.
  exit /b %KIRA_ERR%
)

".venv\Scripts\python.exe" -m examples.three_loop_master_basis_sparse_discovery --family "%FAMILY%" --level "%LEVEL%" --finalize
set "AUDIT_ERR=%ERRORLEVEL%"
if not "%AUDIT_ERR%"=="0" exit /b %AUDIT_ERR%

endlocal
exit /b 0

:usage
echo Usage: %~nx0 FAMILY [LEVEL 0^|1^|2] [fresh]
echo Example plan only:
echo   .venv\Scripts\python.exe -m examples.three_loop_master_basis_sparse_discovery --family Q03_full --level 1 --show-plan
echo Example run:
echo   %~nx0 Q03_full 1 fresh
exit /b 2
