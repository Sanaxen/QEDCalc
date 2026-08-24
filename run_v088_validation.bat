@echo off
setlocal
cd /d %~dp0
set PYTHONPATH=%CD%
echo QEDCalc v0.88 validation
python examples\phase81_ordinary_ladder_end_to_end_checkpoint.py
if errorlevel 1 exit /b 1
python -m pytest -q tests\test_phase81_ordinary_ladder_end_to_end.py
if errorlevel 1 exit /b 1
python -c "import qedcalc; print('QEDCalc', qedcalc.__version__)"
if errorlevel 1 exit /b 1
echo v0.88 validation PASS
endlocal
