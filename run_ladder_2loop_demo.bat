@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" call setup_env.bat
if errorlevel 1 exit /b 1
".venv\Scripts\python.exe" -m examples.ladder_2loop_trial
if errorlevel 1 exit /b 1
echo.
echo Output: output\ladder_2loop_trial.md
pause
