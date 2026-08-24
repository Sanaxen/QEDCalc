@echo off
setlocal EnableExtensions
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (set "PY=.venv\Scripts\python.exe") else (set "PY=python")
set "PYTHONPATH=%CD%"
echo QEDCalc v0.71 validation
%PY% examples\phase57_corner_large_r_overlap_audit.py || goto :fail
%PY% examples\phase58_corner_large_r_cutoff_audit.py || goto :fail
%PY% -m pytest tests\test_corner.py -q || goto :fail
%PY% -c "import qedcalc; print('version:', qedcalc.__version__); assert qedcalc.__version__=='0.71.0'" || goto :fail
echo v0.71 validation PASS
exit /b 0
:fail
echo v0.71 validation FAIL
exit /b 1
