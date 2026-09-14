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

set "PROBE_PY=examples\three_loop_q01_kira_symmetry_relation_probe.py"
if not exist "%PROBE_PY%" (
  echo ERROR: Q01 Kira symmetry relation probe was not found.
  echo Expected: %CD%\%PROBE_PY%
  pause
  exit /b 1
)

".venv\Scripts\python.exe" "%PROBE_PY%"
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (
  echo Q01 Kira symmetry/relation master-form probe PASS
) else (
  echo Q01 Kira symmetry/relation master-form probe FAIL with error code %RC%.
)
pause
exit /b %RC%
