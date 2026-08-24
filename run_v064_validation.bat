@echo off
setlocal EnableExtensions
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (set "PY=.venv\Scripts\python.exe") else (set "PY=python")
set "PYTHONPATH=%CD%"
set "OUT=test_results\v064_%RANDOM%%RANDOM%"
mkdir "%OUT%" >nul 2>&1
>"%OUT%\validation.log" echo QEDCalc v0.64 validation
>>"%OUT%\validation.log" echo Python: %PY%
"%PY%" examples\phase45_corner_eq32_operator_audit.py >"%OUT%\phase45.log" 2>&1
if errorlevel 1 goto :fail
"%PY%" -m pytest tests\test_corner.py -q >"%OUT%\test_corner.log" 2>&1
if errorlevel 1 goto :fail
"%PY%" -c "import qedcalc; print('QEDCalc', qedcalc.__version__)" >"%OUT%\version.log" 2>&1
if errorlevel 1 goto :fail
>>"%OUT%\validation.log" echo v0.64 validation PASS
powershell -NoProfile -Command "Compress-Archive -Path '%OUT%\*' -DestinationPath '%OUT%.zip' -Force" >nul 2>&1
echo v0.64 validation PASS
echo Results: %OUT%.zip
exit /b 0
:fail
>>"%OUT%\validation.log" echo v0.64 validation FAIL
powershell -NoProfile -Command "Compress-Archive -Path '%OUT%\*' -DestinationPath '%OUT%.zip' -Force" >nul 2>&1
type "%OUT%\validation.log"
echo Results: %OUT%.zip
exit /b 1
