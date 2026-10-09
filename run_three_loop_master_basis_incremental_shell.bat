@echo off
setlocal EnableExtensions
cd /d "%~dp0"

if "%~1"=="" goto :usage
if "%~2"=="" goto :usage
if "%~3"=="" goto :usage
if "%~4"=="" goto :usage

set "FAMILY=%~1"
set "FROM_SEED=%~2"
set "TO_SEED=%~3"
set "TOP_SECTOR=%~4"

if not exist ".venv\Scripts\python.exe" (
  echo ERROR: .venv\Scripts\python.exe not found.
  exit /b 1
)

".venv\Scripts\python.exe" -m examples.three_loop_master_basis_incremental_shell ^
  --family "%FAMILY%" ^
  --from-seed "%FROM_SEED%" ^
  --to-seed "%TO_SEED%" ^
  --top-sector "%TOP_SECTOR%" ^
  --include-subsectors

exit /b %ERRORLEVEL%

:usage
echo Usage: %~nx0 FAMILY FROM_SEED TO_SEED TOP_SECTOR
echo Example: %~nx0 VP05_full r8s5d2 r8s6d2 199
exit /b 2
