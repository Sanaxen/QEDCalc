@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set PY=.venv\Scripts\python.exe
) else (
    set PY=py
)

set PYTHONPATH=%CD%;%PYTHONPATH%
%PY% examples\three_loop_q01_boundary_layer_pivot_audit.py
if errorlevel 1 (
    echo Q01 boundary-layer direct-pivot audit FAIL
    exit /b 1
)

echo Q01 boundary-layer direct-pivot audit PASS
exit /b 0
