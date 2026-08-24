@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
set "PY=.venv\Scripts\python.exe"
if not exist "%PY%" set "PY=python"
echo QEDCalc v0.85 validation
"%PY%" examples\phase78_crossed_end_to_end_checkpoint.py || goto :fail
"%PY%" -m pytest -q tests\test_v085_crossed_end_to_end.py || goto :fail
"%PY%" -c "import qedcalc; print('QEDCalc', qedcalc.__version__)" || goto :fail
echo v0.85 validation PASS
exit /b 0
:fail
echo v0.85 validation FAIL
exit /b 1
