@echo off
setlocal
if exist .venv\Scripts\python.exe (set PY=.venv\Scripts\python.exe) else (set PY=python)
set "PYTHONPATH=%CD%"
%PY% examples\phase51_corner_rational_regrouping_audit.py
endlocal
