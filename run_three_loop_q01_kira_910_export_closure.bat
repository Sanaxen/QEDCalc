@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"
set "PYTHONPATH=%CD%"

if not exist ".venv\Scripts\python.exe" (
  echo ERROR: QEDCalc virtual environment was not found.
  echo Expected: %CD%\.venv\Scripts\python.exe
  pause
  exit /b 1
)

where wsl.exe >nul 2>&1
if errorlevel 1 (
  echo ERROR: wsl.exe was not found.
  pause
  exit /b 2
)

wsl.exe bash -lc "command -v kira >/dev/null 2>&1"
if errorlevel 1 (
  echo ERROR: kira was not found in the WSL PATH.
  pause
  exit /b 2
)

wsl.exe bash -lc "test -x $HOME/fermat/Ferl7/fer64"
if errorlevel 1 (
  echo ERROR: Fermat executable was not found or is not executable at $HOME/fermat/Ferl7/fer64.
  pause
  exit /b 3
)

set "PROJECT_WIN=%CD%\output\kira_q01_full_demand_r9s3d0"
set /a PASSNO=0

:LOOP
set /a PASSNO+=1
if !PASSNO! GTR 12 (
  echo ERROR: dependency-closure export exceeded 12 passes.
  pause
  exit /b 4
)

echo.
echo ===== Q01 Kira FORM closure pass !PASSNO! =====
".venv\Scripts\python.exe" examples\three_loop_q01_kira_910_export_closure_generate.py
set "PLANRC=!ERRORLEVEL!"

if "!PLANRC!"=="0" goto DONE
if not "!PLANRC!"=="10" (
  echo Q01 Kira FORM dependency closure planning failed with error code !PLANRC!.
  pause
  exit /b !PLANRC!
)

wsl.exe --cd "%PROJECT_WIN%" bash -lc "set -o pipefail; export FERMATPATH=$HOME/fermat/Ferl7/fer64; kira jobs_export_closure.yaml 2>&1 | tee q01_full_export_closure.log"
set "RC=!ERRORLEVEL!"
if not "!RC!"=="0" (
  echo Q01 Kira FORM closure export failed with error code !RC!.
  pause
  exit /b !RC!
)

goto LOOP

:DONE
echo.
echo Q01 Kira FORM dependency closure PASS
echo No reduction was rerun; only kira2form exports were performed.
pause
exit /b 0
