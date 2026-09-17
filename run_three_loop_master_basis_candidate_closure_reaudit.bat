@echo off
setlocal EnableExtensions
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

echo QEDCalc candidate closure no-rerun re-audit
echo This command does NOT prepare, clean, or rerun Kira projects.
echo It only reads the existing mandatory lists, Kira logs, and masters.final files.
echo.

".venv\Scripts\python.exe" -m examples.three_loop_master_basis_candidate_closure_reaudit --family "%FAMILY%" --baseline-seed "%BASELINE_SEED%" --solver "%SOLVER%"
exit /b %ERRORLEVEL%

:usage
echo Usage: %~nx0 FAMILY BASELINE_SEED [ordinary^|firefly]
echo Example: %~nx0 Q05_full r8s3d0 firefly
exit /b 2
