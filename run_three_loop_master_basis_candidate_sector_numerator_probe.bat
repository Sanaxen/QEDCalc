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

if not exist ".venv\Scripts\python.exe" (
  echo ERROR: .venv\Scripts\python.exe not found.
  exit /b 1
)

".venv\Scripts\python.exe" -m examples.three_loop_master_basis_candidate_sector199_numerator_probe ^
  --family "%FAMILY%" ^
  --baseline-seed "%BASELINE%" ^
  --sector "%SECTOR%" ^
  --max-s "%MAXS%"

exit /b %ERRORLEVEL%

:usage
echo Usage: %~nx0 FAMILY BASELINE_SEED SECTOR MAX_S
echo Example: %~nx0 VP05_full r8s3d0 199 6
exit /b 2
