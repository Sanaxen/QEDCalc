@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" call setup_env.bat
if errorlevel 1 exit /b 1
".venv\Scripts\python.exe" -m examples.self_energy_insertion_2loop_trial
pause
