@echo off
setlocal
cd /d "%~dp0"

set "PYTHONPATH=%CD%;%PYTHONPATH%"

where py >nul 2>&1
if %errorlevel%==0 (
    py -3 examples\three_loop_q01_kira_910_coverage.py
) else (
    python examples\three_loop_q01_kira_910_coverage.py
)

set "RC=%errorlevel%"
echo.
if not "%RC%"=="0" echo Q01 Kira 910 coverage audit failed with error code %RC%.
pause
exit /b %RC%
