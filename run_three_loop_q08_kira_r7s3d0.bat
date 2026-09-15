@echo off
setlocal EnableExtensions
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo ERROR: .venv\Scripts\python.exe not found.
  exit /b 1
)

".venv\Scripts\python.exe" -m examples.three_loop_q08_kira_r7s3d0_audit --prepare
if errorlevel 1 exit /b %ERRORLEVEL%

set "WIN_PROJECT=%CD%\output\kira_q08_full_r7s3d0"
set "WSL_PROJECT="
for /f "usebackq delims=" %%I in (`wsl wslpath -u "%WIN_PROJECT%"`) do set "WSL_PROJECT=%%I"
if not defined WSL_PROJECT (
  echo ERROR: failed to translate Q08 project path into WSL path.
  exit /b 1
)

echo QEDCalc Q08 r7s3d0 Kira run
echo WSL project: %WSL_PROJECT%

wsl bash -lc "set -o pipefail; command -v kira >/dev/null 2>&1 || { echo 'ERROR: kira not found in WSL PATH'; exit 127; }; export FERMATPATH=$HOME/fermat/Ferl7/fer64; [ -x \"$FERMATPATH\" ] || { echo \"ERROR: Fermat executable not found or not executable: $FERMATPATH\"; exit 126; }; echo \"FERMATPATH=$FERMATPATH\"; cd '%WSL_PROJECT%' || exit 2; kira jobs.yaml 2>&1 | tee kira_r7s3d0.log"
set "KIRA_ERR=%ERRORLEVEL%"
if not "%KIRA_ERR%"=="0" (
  echo ERROR: Kira exited with code %KIRA_ERR%.
  exit /b %KIRA_ERR%
)

".venv\Scripts\python.exe" -m examples.three_loop_q08_kira_r7s3d0_audit --finalize
set "AUDIT_ERR=%ERRORLEVEL%"
if not "%AUDIT_ERR%"=="0" exit /b %AUDIT_ERR%

endlocal
