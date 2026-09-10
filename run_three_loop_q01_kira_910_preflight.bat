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

echo.
echo QEDCalc Q01 full-demand Kira preflight
echo project: %PROJECT_WIN%
echo mode: symmetries + initiate only; triangular/back substitution disabled
echo.

wsl.exe bash -lc "command -v kira >/dev/null 2>&1"
if errorlevel 1 (
  echo ERROR: kira was not found in the WSL PATH.
  pause
  exit /b 2
)

rem The previous WSL setup stores Fermat at $HOME/fermat/Ferl7 and appends
rem FERMATPATH to ~/.bashrc.  A non-interactive `bash -lc` does not reliably
rem process ~/.bashrc, so provide the known path explicitly when it is absent.
wsl.exe bash -lc "if [ -z \"${FERMATPATH:-}\" ]; then export FERMATPATH=\"$HOME/fermat/Ferl7\"; fi; if [ ! -x \"$FERMATPATH\" ]; then echo \"ERROR: Fermat executable was not found or is not executable: $FERMATPATH\"; exit 3; fi; echo \"Fermat: $FERMATPATH\""
if errorlevel 1 (
  echo ERROR: Fermat setup check failed in WSL.
  pause
  exit /b 3
)

rem Pass the Windows project path directly to WSL.  Do not round-trip a UTF-8
rem wslpath result through FOR /F, because that corrupts non-ASCII path names
rem under the Windows console code page.  Set FERMATPATH again in the same
rem shell that launches Kira so the variable is guaranteed to be visible.
wsl.exe --cd "%PROJECT_WIN%" bash -lc "set -o pipefail; if [ -z \"${FERMATPATH:-}\" ]; then export FERMATPATH=\"$HOME/fermat/Ferl7\"; fi; echo \"Fermat: $FERMATPATH\"; kira jobs_preflight.yaml 2>&1 | tee q01_full_preflight.log"
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
