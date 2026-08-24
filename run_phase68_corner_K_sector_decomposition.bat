@echo off
setlocal
cd /d %~dp0
if exist .venv\Scripts\python.exe (
  set PY=.venv\Scripts\python.exe
) else (
  set PY=python
)
set PYTHONPATH=%CD%
%PY% run_phase68_corner_K_sector_decomposition.py
endlocal
