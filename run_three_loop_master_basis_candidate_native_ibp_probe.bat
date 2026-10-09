@echo off
setlocal EnableExtensions
cd /d "%~dp0"

if "%~1"=="" goto :usage
if "%~2"=="" goto :usage
if "%~3"=="" goto :usage
if "%~4"=="" goto :usage

set "FAMILY=%~1"
set "BASELINE_SEED=%~2"
set "SECTOR=%~3"
set "DEGREE=%~4"

if not exist ".venv\Scripts\python.exe" (
  echo ERROR: .venv\Scripts\python.exe not found.
  exit /b 1
)

".venv\Scripts\python.exe" -m examples.three_loop_master_basis_candidate_native_ibp_probe ^
  --family "%FAMILY%" ^
  --baseline-seed "%BASELINE_SEED%" ^
  --sector "%SECTOR%" ^
  --degree "%DEGREE%"

exit /b %ERRORLEVEL%

:usage
echo Usage: %~nx0 FAMILY BASELINE_SEED SECTOR DEGREE
echo Example: %~nx0 VP05_full r8s3d0 199 3
exit /b 2
