@echo off
setlocal EnableExtensions
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo ERROR: .venv\Scripts\python.exe not found.
  exit /b 1
)

set "MODE=%~1"
set "ARG2=%~2"
set "ARG3=%~3"
if "%MODE%"=="" set "MODE=plan"

if /I "%MODE%"=="plan" goto :plan
if /I "%MODE%"=="status" goto :status
if /I "%MODE%"=="run" goto :run
if /I "%MODE%"=="resume" goto :resume
goto :usage

:plan
if "%ARG2%"=="" (
  ".venv\Scripts\python.exe" -m examples.three_loop_master_basis_batch_controller --plan
) else if "%ARG3%"=="" (
  ".venv\Scripts\python.exe" -m examples.three_loop_master_basis_batch_controller --plan --start-family "%ARG2%"
) else (
  ".venv\Scripts\python.exe" -m examples.three_loop_master_basis_batch_controller --plan --start-family "%ARG2%" --max-families "%ARG3%"
)
exit /b %ERRORLEVEL%

:status
".venv\Scripts\python.exe" -m examples.three_loop_master_basis_batch_controller --status
exit /b %ERRORLEVEL%

:run
if "%ARG2%"=="" (
  ".venv\Scripts\python.exe" -m examples.three_loop_master_basis_batch_controller --run
) else if "%ARG3%"=="" (
  ".venv\Scripts\python.exe" -m examples.three_loop_master_basis_batch_controller --run --start-family "%ARG2%"
) else (
  ".venv\Scripts\python.exe" -m examples.three_loop_master_basis_batch_controller --run --start-family "%ARG2%" --max-families "%ARG3%"
)
exit /b %ERRORLEVEL%

:resume
if not "%ARG3%"=="" (
  echo ERROR: resume accepts only an optional MAX_FAMILIES argument.
  goto :usage
)
if "%ARG2%"=="" (
  ".venv\Scripts\python.exe" -m examples.three_loop_master_basis_batch_controller --resume
) else (
  ".venv\Scripts\python.exe" -m examples.three_loop_master_basis_batch_controller --resume --max-families "%ARG2%"
)
exit /b %ERRORLEVEL%

:usage
echo Usage:
echo   %~nx0 plan [START_FAMILY] [MAX_FAMILIES]
echo   %~nx0 run [START_FAMILY] [MAX_FAMILIES]
echo   %~nx0 resume [MAX_FAMILIES]
echo   %~nx0 status
echo.
echo Examples:
echo   %~nx0 plan Q12_full 5
echo   %~nx0 run Q12_full 5
echo   %~nx0 status
echo   %~nx0 resume
echo   %~nx0 resume 5
echo.
echo MAX_FAMILIES limits how many canonical families are processed in one unattended batch.
exit /b 2
