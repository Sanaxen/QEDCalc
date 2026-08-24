@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist ".venv\Scripts\python.exe" (
  set "PY=.venv\Scripts\python.exe"
) else (
  set "PY=python"
)
set "OUT=test_results"
if not exist "%OUT%" mkdir "%OUT%"
set "LOG=%OUT%\v063_validation.log"
>"%LOG%" echo QEDCalc v0.63 validation
>>"%LOG%" echo Python: %PY%
"%PY%" examples\phase44_corner_evanescent_os_cancellation.py >>"%LOG%" 2>&1
if errorlevel 1 goto :fail
"%PY%" -m pytest -q tests\test_corner.py >>"%LOG%" 2>&1
if errorlevel 1 goto :fail
"%PY%" -c "import qedcalc; print('version:', qedcalc.__version__)" >>"%LOG%" 2>&1
if errorlevel 1 goto :fail
>>"%LOG%" echo v0.63 validation PASS
powershell -NoProfile -Command "Compress-Archive -Force -Path '%LOG%' -DestinationPath '%OUT%\v063_validation.zip'" >nul 2>&1
echo v0.63 validation PASS
exit /b 0
:fail
>>"%LOG%" echo v0.63 validation FAIL
powershell -NoProfile -Command "Compress-Archive -Force -Path '%LOG%' -DestinationPath '%OUT%\v063_validation.zip'" >nul 2>&1
echo v0.63 validation FAIL
exit /b 1
