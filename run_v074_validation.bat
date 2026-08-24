@echo off
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist ".venv\Scripts\python.exe" (
  set "PY=.venv\Scripts\python.exe"
) else (
  set "PY=python"
)
%PY% run_v074_validation.py > v074_validation.log 2>&1
type v074_validation.log
pause
