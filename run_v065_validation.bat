@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  set "PY=.venv\Scripts\python.exe"
) else (
  set "PY=python"
)
set "PYTHONPATH=%CD%"
set "OUT=test_results\v065_%RANDOM%%RANDOM%"
if not exist test_results mkdir test_results
if exist "%OUT%" rmdir /s /q "%OUT%"
mkdir "%OUT%"
>"%OUT%\v065_validation.log" echo QEDCalc v0.65 validation
>>"%OUT%\v065_validation.log" echo Python: %PY%
"%PY%" examples\phase46_corner_outer_photon_sign.py >>"%OUT%\v065_validation.log" 2>&1
if errorlevel 1 goto :fail
"%PY%" -m pytest -q tests\test_corner.py >>"%OUT%\v065_validation.log" 2>&1
if errorlevel 1 goto :fail
"%PY%" -c "import qedcalc; print('version:', qedcalc.__version__)" >>"%OUT%\v065_validation.log" 2>&1
if errorlevel 1 goto :fail
>>"%OUT%\v065_validation.log" echo v0.65 validation PASS
copy /y "%OUT%\v065_validation.log" "%OUT%\summary.txt" >nul
powershell -NoProfile -Command "Compress-Archive -Path '%OUT%\*' -DestinationPath '%OUT%.zip' -Force" >nul
copy /y "%OUT%.zip" test_results\ >nul
exit /b 0
:fail
>>"%OUT%\v065_validation.log" echo v0.65 validation FAIL
copy /y "%OUT%\v065_validation.log" "%OUT%\summary.txt" >nul
powershell -NoProfile -Command "Compress-Archive -Path '%OUT%\*' -DestinationPath '%OUT%.zip' -Force" >nul
copy /y "%OUT%.zip" test_results\ >nul
exit /b 1
