@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

set "ROOT=%CD%"
set "PYTHONPATH=%ROOT%"

if exist ".venv\Scripts\python.exe" (
  set "PY=.venv\Scripts\python.exe"
) else (
  set "PY=python"
)

if not exist test_results mkdir test_results
for /f "tokens=1-4 delims=/ " %%a in ("%date%") do set "D=%%a%%b%%c%%d"
set "T=%time: =0%"
set "T=%T::=%"
set "T=%T:.=%"
set "STAMP=%D%_%T%"
set "OUT=test_results\v050_%STAMP%"
mkdir "%OUT%"

> "%OUT%\environment.txt" echo ROOT=%ROOT%
>> "%OUT%\environment.txt" echo PYTHONPATH=%PYTHONPATH%
>> "%OUT%\environment.txt" echo PY=%PY%
>> "%OUT%\environment.txt" %PY% --version
>> "%OUT%\environment.txt" %PY% -c "import sympy,pytest; print('SymPy',sympy.__version__); print('pytest',pytest.__version__)"

set "EXITCODE=0"

echo [1/4] Phase 23...
%PY% examples\phase23_crossed_u_tq_bridge_trial.py > "%OUT%\phase23.log" 2>&1
if errorlevel 1 (
  set "EXITCODE=!ERRORLEVEL!"
  type "%OUT%\phase23.log"
  goto :finish
)
type "%OUT%\phase23.log"

echo [2/4] Phase 24...
%PY% examples\phase24_crossed_raw_q_kernel_trial.py > "%OUT%\phase24.log" 2>&1
if errorlevel 1 (
  set "EXITCODE=!ERRORLEVEL!"
  type "%OUT%\phase24.log"
  goto :finish
)
type "%OUT%\phase24.log"

echo [3/4] Phase 25...
%PY% examples\phase25_crossed_automatic_hermite_trial.py > "%OUT%\phase25.log" 2>&1
if errorlevel 1 (
  set "EXITCODE=!ERRORLEVEL!"
  type "%OUT%\phase25.log"
  goto :finish
)
type "%OUT%\phase25.log"

echo [4/4] Full pytest suite...
%PY% -m pytest -vv --durations=100 > "%OUT%\pytest_full.log" 2>&1
if errorlevel 1 set "EXITCODE=!ERRORLEVEL!"
type "%OUT%\pytest_full.log"

:finish
> "%OUT%\exit_code.txt" echo !EXITCODE!

powershell -NoProfile -ExecutionPolicy Bypass -Command "Compress-Archive -Path '%OUT%\*' -DestinationPath '%OUT%.zip' -Force" >nul 2>&1

echo.
echo Validation complete. Exit code: !EXITCODE!
echo Result: %OUT%.zip
pause
exit /b !EXITCODE!
