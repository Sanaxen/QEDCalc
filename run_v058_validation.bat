@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist ".venv\Scripts\python.exe" (set "PY=.venv\Scripts\python.exe") else (set "PY=python")
for /f "tokens=1-4 delims=/-. " %%a in ("%date%") do set DS=%%a%%b%%c
for /f "tokens=1-4 delims=:., " %%a in ("%time%") do set TS=%%a%%b%%c%%d
set "STAMP=%DS%_%TS: =0%"
set "OUT=test_results\v058_%STAMP%"
mkdir "%OUT%" >nul 2>&1
set EXITCODE=0

echo [1/3] Phase 37 outer quadratic bridge...
"%PY%" examples\phase37_corner_outer_quadratic_bridge.py > "%OUT%\phase37.log" 2>&1
set E=!ERRORLEVEL!
type "%OUT%\phase37.log"
if not "!E!"=="0" set EXITCODE=!E!

echo [2/3] Focused v0.58 corner tests...
"%PY%" -m pytest -q tests\test_corner.py > "%OUT%\test_corner.log" 2>&1
set E=!ERRORLEVEL!
type "%OUT%\test_corner.log"
if not "!E!"=="0" set EXITCODE=!E!

echo [3/3] Version...
"%PY%" -c "import qedcalc; print('QEDCalc', qedcalc.__version__)" > "%OUT%\version.log" 2>&1
type "%OUT%\version.log"

if "!EXITCODE!"=="0" (echo v0.58 validation PASS) else (echo v0.58 validation FAIL exit=!EXITCODE!)
> "%OUT%\summary.txt" echo Exit code: !EXITCODE!
>> "%OUT%\summary.txt" echo Expected version: 0.58.0

powershell -NoProfile -ExecutionPolicy Bypass -Command "Compress-Archive -Path '%OUT%\*' -DestinationPath '%OUT%.zip' -Force" >nul 2>&1
echo Result ZIP: %OUT%.zip
exit /b !EXITCODE!
