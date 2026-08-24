@echo off
setlocal
set PY=.venv\Scripts\python.exe
if not exist "%PY%" set PY=python
"%PY%" run_phase74_corner_k2_mass_nonuniform.py
endlocal
