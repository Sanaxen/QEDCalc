@echo off
setlocal EnableExtensions
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (set "PY=.venv\Scripts\python.exe") else (set "PY=python")
set "PYTHONPATH=%CD%"
if not exist test_results mkdir test_results
set "STAMP=%RANDOM%%RANDOM%"
set "OUT=test_results\v062_%STAMP%"
mkdir "%OUT%"
"%PY%" examples\phase43_corner_dimensional_radial_audit.py > "%OUT%\phase43.log" 2>&1
if errorlevel 1 goto :fail
"%PY%" -m pytest -q tests\test_corner.py > "%OUT%\test_corner.log" 2>&1
if errorlevel 1 goto :fail
"%PY%" -c "import qedcalc; print('QEDCalc',qedcalc.__version__)" > "%OUT%\version.log" 2>&1
if errorlevel 1 goto :fail
echo v0.62 validation PASS> "%OUT%\summary.txt"
powershell -NoProfile -Command "Compress-Archive -Path '%OUT%\*' -DestinationPath '%OUT%.zip' -Force"
echo PASS: %OUT%.zip
exit /b 0
:fail
echo v0.62 validation FAIL> "%OUT%\summary.txt"
powershell -NoProfile -Command "Compress-Archive -Path '%OUT%\*' -DestinationPath '%OUT%.zip' -Force"
echo FAIL: %OUT%.zip
exit /b 1
