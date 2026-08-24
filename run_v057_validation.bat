@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"
set "ROOT=%CD%"
set "PYTHONPATH=%ROOT%"
if exist ".venv\Scripts\python.exe" (set "PY=.venv\Scripts\python.exe") else (set "PY=python")
for /f "tokens=1-4 delims=/ " %%a in ('date /t') do set DATESTAMP=%%a%%b%%c%%d
set TIMESTAMP=%TIME: =0%
set TIMESTAMP=%TIMESTAMP::=%
set TIMESTAMP=%TIMESTAMP:.=%
set "OUT=test_results\v057_%DATESTAMP%_%TIMESTAMP%"
mkdir "%OUT%" >nul 2>&1
"%PY%" -c "import qedcalc; print('QEDCalc',qedcalc.__version__)" > "%OUT%\version.log" 2>&1

echo [1/3] Phase 36 renormalized inner vertex...
"%PY%" examples\phase36_corner_renormalized_inner_vertex_bridge.py > "%OUT%\phase36.log" 2>&1
if errorlevel 1 goto :fail
type "%OUT%\phase36.log"

echo [2/3] Focused v0.57 corner tests...
"%PY%" -m pytest -q tests\test_corner.py -k "v057 or v056" > "%OUT%\focused.log" 2>&1
if errorlevel 1 goto :fail
type "%OUT%\focused.log"

echo [3/3] Full corner regression...
"%PY%" -m pytest -q tests\test_corner.py > "%OUT%\corner_full.log" 2>&1
if errorlevel 1 goto :fail
type "%OUT%\corner_full.log"

echo v0.57 validation PASS > "%OUT%\summary.txt"
powershell -NoProfile -Command "Compress-Archive -Path '%OUT%\*' -DestinationPath '%OUT%.zip' -Force"
echo Result ZIP: %OUT%.zip
exit /b 0
:fail
echo v0.57 validation FAIL > "%OUT%\summary.txt"
powershell -NoProfile -Command "Compress-Archive -Path '%OUT%\*' -DestinationPath '%OUT%.zip' -Force"
echo Result ZIP: %OUT%.zip
exit /b 1
