@echo off
setlocal
if exist .venv\Scripts\python.exe (
  set PY=.venv\Scripts\python.exe
) else (
  set PY=python
)
set "PYTHONPATH=%CD%"
%PY% -c "import qedcalc; print('version', qedcalc.__version__)"
if errorlevel 1 exit /b 1
%PY% examples\phase50_corner_K_convention_resolved_audit.py
if errorlevel 1 exit /b 1
%PY% examples\phase51_corner_rational_regrouping_audit.py
if errorlevel 1 exit /b 1
%PY% -m pytest tests\test_corner.py -q
if errorlevel 1 exit /b 1
endlocal
