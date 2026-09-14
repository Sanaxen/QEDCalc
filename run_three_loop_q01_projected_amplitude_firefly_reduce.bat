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

set "REDUCE_PY=examples\three_loop_q01_projected_amplitude_firefly_reduce.py"
if not exist "%REDUCE_PY%" (
  echo ERROR: Q01 projected-amplitude FireFly reduction helper was not found.
  echo Expected: %CD%\%REDUCE_PY%
  pause
  exit /b 1
)

".venv\Scripts\python.exe" "%REDUCE_PY%"
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (
  echo Q01 projected-amplitude FireFly reduction PASS
) else (
  echo Q01 projected-amplitude FireFly reduction FAIL with error code %RC%.
)
pause
exit /b %RC%
