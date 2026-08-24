@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Virtual environment was not found. Running setup_env.bat first.
  call setup_env.bat
  if errorlevel 1 exit /b 1
)
".venv\Scripts\python.exe" -m examples.conventions_demo
if errorlevel 1 (
  echo.
  echo Conventions demo failed.
  pause
  exit /b 1
)
echo.
echo Conventions demo completed.
pause
