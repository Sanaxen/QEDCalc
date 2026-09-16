@echo off
setlocal EnableExtensions
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo ERROR: .venv\Scripts\python.exe not found.
  exit /b 1
)

for %%S in (r10s4d2 r9s5d2 r9s4d3) do (
  echo.
  echo ============================================================
  echo QEDCalc Q02 final17 FireFly boundary %%S
  echo ============================================================
  ".venv\Scripts\python.exe" -m examples.three_loop_q02_firefly_final17_boundary_audit --seed %%S --prepare
  if errorlevel 1 exit /b %ERRORLEVEL%

  set "WIN_PROJECT=%CD%\output\kira_q02_full_firefly_final17_%%S"
  wsl.exe --cd "!WIN_PROJECT!" bash -lc "set -o pipefail; command -v kira >/dev/null 2>&1 || { echo 'ERROR: kira not found in WSL PATH'; exit 127; }; rm -rf firefly_saves ff_save firefly_saves_alt; export FERMATPATH=$HOME/fermat/Ferl7/fer64; echo FERMATPATH=$FERMATPATH; kira jobs.yaml 2>&1 | tee q02_firefly_final17_%%S.log"
  if errorlevel 1 exit /b %ERRORLEVEL%

  ".venv\Scripts\python.exe" -m examples.three_loop_q02_firefly_final17_boundary_audit --seed %%S --finalize
  if errorlevel 1 exit /b %ERRORLEVEL%
)

".venv\Scripts\python.exe" -m examples.three_loop_q02_firefly_final17_boundary_audit --aggregate
if errorlevel 1 exit /b %ERRORLEVEL%

endlocal
