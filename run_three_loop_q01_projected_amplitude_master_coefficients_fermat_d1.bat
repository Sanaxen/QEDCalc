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

where wsl.exe >nul 2>&1
if errorlevel 1 (
  echo ERROR: wsl.exe was not found.
  pause
  exit /b 2
)

wsl.exe bash -lc "test -x $HOME/fermat/Ferl7/fer64"
if errorlevel 1 (
  echo ERROR: Fermat executable was not found or is not executable at $HOME/fermat/Ferl7/fer64.
  pause
  exit /b 4
)

set "HELPER=examples\three_loop_q01_projected_amplitude_master_coefficients_fermat_d1.py"
if not exist "%HELPER%" (
  echo ERROR: d+1 Fermat coefficient-synthesis helper was not found.
  pause
  exit /b 1
)

echo.
echo QEDCalc Q01 projected-amplitude -^> final60 master coefficient synthesis [FERMAT d+1]
echo mode: saved projected amplitude + saved r9s3d1 FireFly reduction; no new Kira run
echo expected reduction masters.final: 60
echo.

".venv\Scripts\python.exe" "%HELPER%"
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (
  echo Q01 d+1 Fermat coefficient synthesis PASS
) else (
  echo Q01 d+1 Fermat coefficient synthesis FAIL with error code %RC%.
)
pause
exit /b %RC%
