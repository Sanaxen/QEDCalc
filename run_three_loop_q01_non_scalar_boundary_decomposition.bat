@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set PY=.venv\Scripts\python.exe
) else (
    set PY=py
)

set "PYTHONPATH=%CD%;%PYTHONPATH%"
%PY% examples\three_loop_q01_non_scalar_boundary_decomposition.py
if errorlevel 1 (
    echo Q01 non-scalar terminal boundary decomposition FAIL
    exit /b 1
)

echo Q01 non-scalar terminal boundary decomposition PASS
exit /b 0
