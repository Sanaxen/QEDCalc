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

rem Resolve the actual Fermat executable.  The previous setup stored
rem FERMATPATH=$HOME/fermat/Ferl7, which may be either the executable itself
rem or a directory containing fer64/Ferl7/fermat.
wsl.exe bash -lc "source ~/.bashrc >/dev/null 2>&1 || true; base=${FERMATPATH:-$HOME/fermat/Ferl7}; f=; if [ -f $base ] && [ -x $base ]; then f=$base; elif [ -x $base/fer64 ]; then f=$base/fer64; elif [ -x $base/Ferl7 ]; then f=$base/Ferl7; elif [ -x $base/fermat ]; then f=$base/fermat; elif [ -x $HOME/fermat/fer64 ]; then f=$HOME/fermat/fer64; elif [ -x $HOME/fermat/Ferl7/fer64 ]; then f=$HOME/fermat/Ferl7/fer64; fi; if [ -z $f ]; then echo ERROR: no executable Fermat binary was resolved.; echo Configured FERMATPATH: $base; ls -ld $base 2>/dev/null || true; if [ -d $base ]; then echo Directory contents:; ls -la $base 2>/dev/null | head -30; fi; exit 3; fi; echo Fermat: $f"
if errorlevel 1 (
  echo ERROR: Fermat setup check failed in WSL.
  pause
  exit /b 3
)

rem Pass the Windows project path directly to WSL.  Do not round-trip a UTF-8
rem wslpath result through FOR /F, because that corrupts non-ASCII path names
rem under the Windows console code page.  Resolve and export the Fermat binary
rem again in the same Bash process that launches Kira.
wsl.exe --cd "%PROJECT_WIN%" bash -lc "set -o pipefail; source ~/.bashrc >/dev/null 2>&1 || true; base=${FERMATPATH:-$HOME/fermat/Ferl7}; f=; if [ -f $base ] && [ -x $base ]; then f=$base; elif [ -x $base/fer64 ]; then f=$base/fer64; elif [ -x $base/Ferl7 ]; then f=$base/Ferl7; elif [ -x $base/fermat ]; then f=$base/fermat; elif [ -x $HOME/fermat/fer64 ]; then f=$HOME/fermat/fer64; elif [ -x $HOME/fermat/Ferl7/fer64 ]; then f=$HOME/fermat/Ferl7/fer64; fi; if [ -z $f ]; then echo ERROR: no executable Fermat binary was resolved.; exit 3; fi; export FERMATPATH=$f; echo Fermat: $FERMATPATH; kira jobs_preflight.yaml 2>&1 | tee q01_full_preflight.log"
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
