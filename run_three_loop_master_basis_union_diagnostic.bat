@echo off
setlocal EnableExtensions
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo ERROR: .venv\Scripts\python.exe not found.
  exit /b 1
)
set "FAMILY=%~1"
set "SEED=%~2"
if "%FAMILY%"=="" set "FAMILY=Q18_full"
if "%SEED%"=="" set "SEED=r8s3d0"
".venv\Scripts\python.exe" -m examples.three_loop_master_basis_union_diagnostic --family "%FAMILY%" --baseline-seed "%SEED%" --solver firefly
exit /b %ERRORLEVEL%
