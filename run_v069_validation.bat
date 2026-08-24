@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    set "PY=.venv\Scripts\python.exe"
) else (
    set "PY=python"
)
set "PYTHONPATH=%CD%"
set "OUT=test_results\v069_validation"
if not exist "%OUT%" mkdir "%OUT%"
"%PY%" -c "import qedcalc; print('QEDCalc', qedcalc.__version__)" > "%OUT%\version.log" 2>&1
if errorlevel 1 goto :fail
"%PY%" examples\phase52_corner_log_unsplit_audit.py > "%OUT%\phase52.log" 2>&1
if errorlevel 1 goto :fail
"%PY%" examples\phase53_corner_soft_importance_audit.py > "%OUT%\phase53.log" 2>&1
if errorlevel 1 goto :fail
"%PY%" examples\phase54_corner_B_finite_normalization_audit.py > "%OUT%\phase54.log" 2>&1
if errorlevel 1 goto :fail
"%PY%" -m pytest -q tests\test_corner.py > "%OUT%\pytest_corner.log" 2>&1
if errorlevel 1 goto :fail
(
 echo v0.69 validation PASS
 type "%OUT%\version.log"
 type "%OUT%\phase52.log"
 type "%OUT%\phase53.log"
 type "%OUT%\phase54.log"
 type "%OUT%\pytest_corner.log"
) > "%OUT%\summary.txt"
type "%OUT%\summary.txt"
exit /b 0
:fail
(
 echo v0.69 validation FAIL
 if exist "%OUT%\version.log" type "%OUT%\version.log"
 if exist "%OUT%\phase52.log" type "%OUT%\phase52.log"
 if exist "%OUT%\phase53.log" type "%OUT%\phase53.log"
 if exist "%OUT%\phase54.log" type "%OUT%\phase54.log"
 if exist "%OUT%\pytest_corner.log" type "%OUT%\pytest_corner.log"
) > "%OUT%\summary.txt"
type "%OUT%\summary.txt"
exit /b 1
