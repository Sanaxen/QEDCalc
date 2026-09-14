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

set "PROBE=examples\three_loop_q01_kira_sector_permutation_equivalence_probe.py"
if not exist "%PROBE%" (
  echo ERROR: Q01 Kira sector-permutation equivalence probe was not found.
  echo Expected: %CD%\%PROBE%
  pause
  exit /b 1
)

".venv\Scripts\python.exe" "%PROBE%"
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (
  echo Q01 Kira sector-permutation master-form equivalence probe PASS
) else (
  echo Q01 Kira sector-permutation master-form equivalence probe FAIL with error code %RC%.
)
pause
exit /b %RC%
