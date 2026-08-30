@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

set "PYTHON=python"
if exist ".venv\Scripts\python.exe" set "PYTHON=.venv\Scripts\python.exe"

for /f "tokens=1-4 delims=/ " %%a in ("%date%") do set "DATEPART=%%a%%b%%c%%d"
set "TIMEPART=%time: =0%"
set "TIMEPART=%TIMEPART::=%"
set "TIMEPART=%TIMEPART:.=%"
set "STAMP=%DATEPART%_%TIMEPART%"
set "OUTDIR=test_results\v050_%STAMP%"
mkdir "%OUTDIR%" >nul 2>&1

(
  echo QEDCalc v0.50.0 full validation
  echo Date: %date% %time%
  echo Root: %cd%
  echo.
  "%PYTHON%" --version
  "%PYTHON%" -c "import sympy,pytest; print('SymPy',sympy.__version__); print('pytest',pytest.__version__)"
) > "%OUTDIR%\environment.txt" 2>&1

call :run phase23 "%PYTHON%" examples\phase23_crossed_u_tq_bridge_trial.py
if errorlevel 1 goto :finish
call :run phase24 "%PYTHON%" examples\phase24_crossed_raw_q_kernel_trial.py
if errorlevel 1 goto :finish
call :run phase25 "%PYTHON%" examples\phase25_crossed_automatic_hermite_trial.py
if errorlevel 1 goto :finish

"%PYTHON%" -m pytest -vv --durations=100 > "%OUTDIR%\pytest_full.log" 2>&1
set "RC=%ERRORLEVEL%"

:finish
if not defined RC set "RC=%ERRORLEVEL%"
echo %RC%> "%OUTDIR%\exit_code.txt"
(
  echo Exit code: %RC%
  echo.
  echo === Phase 23 ===
  if exist "%OUTDIR%\phase23.log" type "%OUTDIR%\phase23.log"
  echo.
  echo === Phase 24 ===
  if exist "%OUTDIR%\phase24.log" type "%OUTDIR%\phase24.log"
  echo.
  echo === Phase 25 ===
  if exist "%OUTDIR%\phase25.log" type "%OUTDIR%\phase25.log"
  echo.
  if exist "%OUTDIR%\pytest_full.log" (
    echo === pytest tail ===
    powershell -NoProfile -Command "Get-Content -LiteralPath '%OUTDIR%\pytest_full.log' -Tail 80"
  )
) > "%OUTDIR%\summary.txt" 2>&1

set "ZIP=%OUTDIR%.zip"
powershell -NoProfile -Command "Compress-Archive -Path '%OUTDIR%\*' -DestinationPath '%ZIP%' -Force"
echo.
echo Validation complete. Exit code: %RC%
echo Please send this file back to ChatGPT:
echo %ZIP%
pause
exit /b %RC%

:run
set "NAME=%~1"
shift
%* > "%OUTDIR%\%NAME%.log" 2>&1
set "STEP_RC=%ERRORLEVEL%"
if not "%STEP_RC%"=="0" (
  set "RC=%STEP_RC%"
  exit /b %STEP_RC%
)
exit /b 0
