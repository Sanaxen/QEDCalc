@echo off
setlocal EnableExtensions
cd /d "%~dp0"

if "%~1"=="" goto :usage
if "%~2"=="" goto :usage
if "%~3"=="" goto :usage

set "FAMILY=%~1"
set "BASELINE_SEED=%~2"
set "SECTOR=%~3"
set "MAX_DEGREE=%~4"
set "BATCH_SIZE=%~5"

if "%MAX_DEGREE%"=="" set "MAX_DEGREE=6"
if "%BATCH_SIZE%"=="" set "BATCH_SIZE=250"

if not exist ".venv\Scripts\python.exe" (
  echo ERROR: .venv\Scripts\python.exe not found.
  exit /b 1
)

".venv\Scripts\python.exe" -m examples.three_loop_master_basis_candidate_incremental_native_ibp ^
  --family "%FAMILY%" ^
  --baseline-seed "%BASELINE_SEED%" ^
  --sector "%SECTOR%" ^
  --max-degree "%MAX_DEGREE%" ^
  --batch-size "%BATCH_SIZE%"

exit /b %ERRORLEVEL%

:usage
echo Usage: %~nx0 FAMILY BASELINE_SEED SECTOR [MAX_DEGREE] [BATCH_SIZE]
echo Example: %~nx0 VP05_full r8s3d0 199 6 250
exit /b 2
