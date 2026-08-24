@echo off
setlocal
cd /d "%~dp0"
set PY=.venv\Scripts\python.exe
if not exist "%PY%" set PY=python
set PYTHONPATH=%CD%
echo QEDCalc v0.87 validation
"%PY%" examples\phase80_self_energy_end_to_end_checkpoint.py || goto :fail
"%PY%" -m pytest -q tests\test_v087_self_energy_end_to_end.py || goto :fail
"%PY%" -c "import qedcalc; print('QEDCalc', qedcalc.__version__)" || goto :fail
echo v0.87 validation PASS
exit /b 0
:fail
echo v0.87 validation FAIL
exit /b 1
