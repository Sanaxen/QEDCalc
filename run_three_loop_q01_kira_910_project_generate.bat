@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"

if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" examples\three_loop_q01_kira_910_project_generate.py
) else (
  python examples\three_loop_q01_kira_910_project_generate.py
)

set "RC=%ERRORLEVEL%"
echo.
if not "%RC%"=="0" echo Q01 full-demand Kira project generation failed with error code %RC%.
pause
exit /b %RC%
