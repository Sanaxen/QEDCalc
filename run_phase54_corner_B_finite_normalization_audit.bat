@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    set "PY=.venv\Scripts\python.exe"
) else (
    set "PY=python"
)
set "PYTHONPATH=%CD%"
"%PY%" examples\phase54_corner_B_finite_normalization_audit.py
endlocal
