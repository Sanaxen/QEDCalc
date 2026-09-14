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

set "HELPER=examples\three_loop_q01_projected_amplitude_master_coefficients.py"
if not exist "%HELPER%" (
  echo ERROR: Q01 master-coefficient synthesis helper was not found.
  echo Expected: %CD%\%HELPER%
  pause
  exit /b 1
)

echo.
echo QEDCalc Q01 projected-amplitude to final60 master coefficient synthesis
echo mode: saved artifacts only; no new projected trace or Kira reduction
echo.

".venv\Scripts\python.exe" "%HELPER%"
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (
  echo Q01 projected-amplitude final60 master coefficient synthesis PASS
) else (
  echo Q01 projected-amplitude final60 master coefficient synthesis FAIL with error code %RC%.
)
pause
exit /b %RC%
