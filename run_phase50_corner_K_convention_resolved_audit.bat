@echo off
setlocal
if exist .venv\Scripts\python.exe (set PY=.venv\Scripts\python.exe) else (set PY=python)
set "PYTHONPATH=%CD%"
%PY% examples\phase50_corner_K_convention_resolved_audit.py
endlocal
