@echo off
setlocal EnableExtensions
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo ERROR: .venv\Scripts\python.exe not found.
  exit /b 1
)

set "MODE=%~1"
set "START=%~2"
if "%MODE%"=="" set "MODE=plan"

if /I "%MODE%"=="plan" goto :plan
if /I "%MODE%"=="status" goto :status
if /I "%MODE%"=="run" goto :run
if /I "%MODE%"=="resume" goto :run
goto :usage

:plan
if "%START%"=="" (
  ".venv\Scripts\python.exe" -m examples.three_loop_master_basis_batch_controller --plan
) else (
  ".venv\Scripts\python.exe" -m examples.three_loop_master_basis_batch_controller --plan --start-family "%START%"
)
exit /b %ERRORLEVEL%

:status
".venv\Scripts\python.exe" -m examples.three_loop_master_basis_batch_controller --status
exit /b %ERRORLEVEL%

:run
if "%START%"=="" (
  ".venv\Scripts\python.exe" -m examples.three_loop_master_basis_batch_controller --run
) else (
  ".venv\Scripts\python.exe" -m examples.three_loop_master_basis_batch_controller --run --start-family "%START%"
)
exit /b %ERRORLEVEL%

:usage
echo Usage: %~nx0 [plan^|status^|run^|resume] [START_FAMILY]
echo.
echo Examples:
echo   %~nx0 plan
echo   %~nx0 plan Q05_full
echo   %~nx0 run Q05_full
echo   %~nx0 status
echo   %~nx0 resume Q09_full
exit /b 2
