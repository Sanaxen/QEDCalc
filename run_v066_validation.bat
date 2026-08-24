@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  set "PY=.venv\Scripts\python.exe"
) else (
  set "PY=python"
)
set "PYTHONPATH=%CD%"
set "OUT=test_results"
if not exist "%OUT%" mkdir "%OUT%"
>"%OUT%\v066_validation.log" echo QEDCalc v0.66 validation
>>"%OUT%\v066_validation.log" echo Python: %PY%
"%PY%" examples\phase48_corner_sequential_family_audit.py >>"%OUT%\v066_validation.log" 2>&1 || goto :fail
"%PY%" -m pytest -q tests\test_corner.py >>"%OUT%\v066_validation.log" 2>&1 || goto :fail
"%PY%" -c "import qedcalc; print('version:',qedcalc.__version__)" >>"%OUT%\v066_validation.log" 2>&1 || goto :fail
>>"%OUT%\v066_validation.log" echo v0.66 validation PASS
type "%OUT%\v066_validation.log"
exit /b 0
:fail
>>"%OUT%\v066_validation.log" echo v0.66 validation FAIL
type "%OUT%\v066_validation.log"
exit /b 1
