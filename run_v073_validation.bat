@echo off
setlocal EnableExtensions
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (set "PY=.venv\Scripts\python.exe") else (set "PY=python")
set "PYTHONPATH=%CD%"
echo QEDCalc v0.73 validation
%PY% examples\phase59_corner_overlap_add_subtract.py || goto :fail
%PY% examples\phase60_corner_joint_soft_density.py || goto :fail
%PY% -m pytest tests\test_corner.py -q || goto :fail
%PY% -c "import qedcalc; print('version:', qedcalc.__version__); assert qedcalc.__version__=='0.73.0'" || goto :fail
echo v0.73 validation PASS
exit /b 0
:fail
echo v0.73 validation FAIL
exit /b 1
