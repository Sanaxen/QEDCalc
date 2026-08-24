@echo off
setlocal
cd /d "%~dp0"
set "PY=python"
if exist ".venv\Scripts\python.exe" set "PY=.venv\Scripts\python.exe"
set "PYTHONPATH=%CD%"
if not exist output mkdir output
"%PY%" -c "import qedcalc; print('QEDCalc', qedcalc.__version__)" > output\version.log 2>&1
"%PY%" examples\phase64_corner_finite_rho_qmc.py --rho 0.05 --power 10 --seed 1 > output\phase64.log 2>&1
"%PY%" -m pytest -q tests\test_corner.py::test_phase64_finite_rho_numerical_measure_ownership_is_exact > output\phase64_test.log 2>&1
if errorlevel 1 exit /b 1
echo QEDCalc v0.75 validation PASS
endlocal
