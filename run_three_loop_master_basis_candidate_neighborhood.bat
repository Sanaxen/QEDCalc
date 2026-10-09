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
set "FROM_SEED=%~3"
set "TO_SEED=%~4"
set "SECTOR=%~5"
set "RADIUS=%~6"
if "%RADIUS%"=="" set "RADIUS=2"

if not exist ".venv\Scripts\python.exe" (
  echo ERROR: .venv\Scripts\python.exe not found.
  exit /b 1
)

".venv\Scripts\python.exe" -m examples.three_loop_master_basis_candidate_neighborhood ^
  --family "%FAMILY%" ^
  --baseline-seed "%BASELINE_SEED%" ^
  --from-seed "%FROM_SEED%" ^
  --to-seed "%TO_SEED%" ^
  --sector "%SECTOR%" ^
  --radius "%RADIUS%"

exit /b %ERRORLEVEL%

:usage
echo Usage: %~nx0 FAMILY BASELINE_SEED FROM_SEED TO_SEED SECTOR [RADIUS]
echo Example: %~nx0 VP05_full r8s3d0 r8s5d2 r8s6d2 199 2
exit /b 2
