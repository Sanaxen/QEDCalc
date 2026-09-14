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

set "FINALIZE_PY=examples\three_loop_q01_projected_amplitude_master_finalize.py"
if not exist "%FINALIZE_PY%" (
  echo ERROR: Q01 projected-amplitude master finalizer was not found.
  echo Expected: %CD%\%FINALIZE_PY%
  pause
  exit /b 1
)

".venv\Scripts\python.exe" "%FINALIZE_PY%"
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (
  echo Q01 projected-amplitude Kira-master finalization PASS
) else (
  echo Q01 projected-amplitude Kira-master finalization FAIL with error code %RC%.
)
pause
exit /b %RC%
