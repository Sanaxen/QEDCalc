@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Virtual environment not found. Run setup_env.bat first.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m examples.phase8_three_probe_full_degree3_trial
if errorlevel 1 (
  echo Phase-8 full degree-3 audit failed.
  pause
  exit /b 1
)
echo.
echo Phase-8 full degree-3 audit completed.
pause
