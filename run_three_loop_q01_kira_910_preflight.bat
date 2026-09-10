@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"

if not exist ".venv\Scripts\python.exe" (
  echo ERROR: QEDCalc virtual environment was not found.
  echo Expected: %CD%\.venv\Scripts\python.exe
  pause
  exit /b 1
)

".venv\Scripts\python.exe" examples\three_loop_q01_kira_910_preflight_generate.py
if errorlevel 1 (
  set "RC=%ERRORLEVEL%"
  echo.
  echo Q01 Kira preflight job generation failed with error code %RC%.
  pause
  exit /b %RC%
)

where wsl.exe >nul 2>&1
if errorlevel 1 (
  echo ERROR: wsl.exe was not found.
  pause
  exit /b 2
)

set "PROJECT_WIN=%CD%\output\kira_q01_full_demand_r9s3d0"
for /f "usebackq delims=" %%I in (`wsl.exe wslpath -a "%PROJECT_WIN%"`) do set "PROJECT_WSL=%%I"

if not defined PROJECT_WSL (
  echo ERROR: failed to translate the Kira project path to a WSL path.
  pause
  exit /b 2
)

echo.
echo QEDCalc Q01 full-demand Kira preflight
echo project: %PROJECT_WIN%
echo WSL project: %PROJECT_WSL%
echo mode: symmetries + initiate only; triangular/back substitution disabled
echo.

wsl.exe bash -lc "command -v kira >/dev/null 2>&1"
if errorlevel 1 (
  echo ERROR: kira was not found in the WSL PATH.
  pause
  exit /b 2
)

wsl.exe bash -lc "set -o pipefail; cd \"%PROJECT_WSL%\" && kira jobs_preflight.yaml 2>&1 | tee q01_full_preflight.log"
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (
  echo Q01 full-demand Kira preflight PASS
  echo log: %PROJECT_WIN%\q01_full_preflight.log
) else (
  echo Q01 full-demand Kira preflight failed with error code %RC%.
)
pause
exit /b %RC%
