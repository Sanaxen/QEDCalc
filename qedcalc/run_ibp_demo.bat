@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo QEDCalc virtual environment was not found.
  echo Run setup_env.bat first.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m examples.ibp_laporta_trial
if errorlevel 1 (
  echo.
  echo IBP / Laporta demo failed.
  pause
  exit /b 1
)
echo.
echo IBP / Laporta demo completed.
echo See output\ibp_laporta_trial.md
pause
endlocal
